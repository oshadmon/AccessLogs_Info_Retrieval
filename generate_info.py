import datetime
import googlemaps
import os
import pymysql
import re
import requests
import sys
import threading

from json import dumps
from pygeocoder import Geocoder
import sys

from github import GitHub 
from location_info import LocationInfo
from read_file import InfoFromFile 

class GenerateInfo: 
   def __init__(self, *args): 
      """
      Generate regarding viistors either from file or GitHub
      """
      self._declare_values(values=sys.argv)
      conn = pymysql.connect(host=self.host, port=self.port,  user=self.user, password=self.password, db=self.db, autocommit=True)
      self.c = conn.cursor()

   def _declare_values(self, values:list=[]): 
      """
      Based on user input set variables 
      :args: 
         # database config & "generic" config  
         self.host:str       - database host 
         self.port:int       - database port  
         self.user:str       - database user 
         self.passwd:str     - database password 
         self.db:str         - database name 
         self.source:str     - source from which data is derived 

         # GitHub required config 
         self.auth:str       - GitHub Authentication info 
         self.org:str        - Organization that repo falls under 
         self.repo:str       - Git Repository (if relevent) 
         
         # Non Git config 
         self.file_name:str  - file containing source info  (for non-Git sources)
         self.downloads:bool - only store download results 
         self.traffic:bool   - only store traffic results   
         
         Note if neither downloads or traffic is set, then execute both 
      """
      self.host='localhost' 
      self.port=3306 
      self.user='root' 
      self.password=''
      self.db='test'
      self.source='NewSource'
      self.auth="('user@githbu.com', 'pass')" # GitHub user and password info code (if statement adds parentheses)  
      self.org='NewOrg' # GitHub repository (if set to 'NewOrg' then uses GitHub user instead)  
      self.repo='NewRepo' # Git Repository 
      self.file_name='/tmp/output.txt' # For none Git sources  
      self.downloads=True
      self.traffic=True

      for value in values: 
         if value is sys.argv[0]: 
            pass 
         if "--host" in value: 
            self.host = str(value.split("=")[-1].split(":")[0])
            self.port = int(value.split("=")[-1].split(":")[1])
         elif "--user" in value: 
            self.user     = str(value.split("=")[-1].split(":")[0])
            self.password = str(value.split("=")[-1].split(":")[1])  
         elif "--db" in value: 
            self.db = str(value.split("=")[-1])
         elif "--source" in value: 
            self.source = str(value.split("=")[-1]) 
         elif "--auth" in value:
            self.auth = "("+str(value.split("=")[-1])+")"
         elif "--org" in value: 
            self.org = str(value.split("=")[-1])
         elif "--repo" in value: 
            self.repo = str(value.split("=")[-1]) 
         elif "--file-name" in value: 
            self.file_name = str(value.split("=")[-1])
         elif "--download" in value: 
            self.traffic = False 
         elif "--traffic" in value: 
            self.downloads = False 
         else: 
            pass  

         if self.org is "NewOrg":
            self.org = self.auth.split("(")[1].split(",")[0].split("@")[0] 
 
   def main(self): 
      if self.source.lower() in ['aws', 'website']: 
         gii = GenerateIPBasedInfo(cur=self.c, file_name=self.file_name, source=self.source) 
         if self.downloads is True: 
            gii.download_ip() 
         if self.traffic is True: 
            gii.traffic_ip() 

      if self.source.lower() is 'github':
         gh = GenerateGitHubInfo(cur=self.c, auth=self.auth, org=self.org, repo=self.repo) 
         gh.github() 
         

class GenerateIPBasedInfo: 
   def __init__(self, cur:pymysql.cursors.Cursor=None, file_name:str='/tmp/output.txt', source='NewSource'): 
      """
      The following class uses a files, containing IP and timestamps, to generate insight regarding visitors
      :args: 
         self.c:pymysql.cursors.Cursor - MySQL connection cursor 
         self.file_name:str - file path with data 
         self.source:str - source where data is from (AWS, Website, etc.)) 
      """
      self.c = cur 
      self.file_name = file_name
      self.source=source 

   def download_ip(self): 
      """
      Generate information from file that contains download information
      """
      iff = InfoFromFile(file_name=self.file_name) 
      self.ip_data, self.timestamp_data = iff.itterate_file() # Get Information from File
      threads=[]
      for ip in self.ip_data: # Get other information
        threads.append(threading.Thread(target=self._generate_location_info, args=(ip,)))
      for t in threads:
         t.start()
      for t in threads:
         t.join()
      self._send_to_ip_data() 
      self._send_to_download() 

   def traffic_ip(self):
      """ 
      Generate information from file that contains traffic information
      """
      iff = InfoFromFile(file_name=self.file_name)
      self.ip_data, self.timestamp_data = iff.itterate_file() # Get Information from File
      threads=[]
      for ip in self.ip_data: # Get other information
        threads.append(threading.Thread(target=self._generate_location_info, args=(ip,)))
      for t in threads:
         t.start()
      for t in threads:
         t.join()
      self._send_to_ip_data()
      self._send_to_traffic()


   def _generate_location_info(self, ip:str='127.0.0.1'):
      """
      Commands to generate information about a given IP address 
      :args: 
         ip:str - IP address which is analyzed 
      """
      li = LocationInfo(ip=ip, api_key='AIzaSyA2wFqcg5NG3CiQDIevIVvBmAK-rQxjp8U', query='VC', radius=0)
      self.ip_data[ip]['coordinates'] = li.get_lat_long()
      self.ip_data[ip]['address'] = li.get_address()
      self.ip_data[ip]['places'] = li.get_possible_places()

   def _send_to_ip_data(self):
      """
      Insert into ip_data `ip_data` in details rather than a JSON object 
      """
      check_row="SELECT COUNT(*) FROM ip_data WHERE ip='%s' AND source='%s';"
      insert_stmt=("INSERT INTO ip_data(create_timestamp, update_timestamp, ip, source, total_access, access_times, coordiantes, address, places) VALUES " 
                  +"('%s', NOW(), '%s', '%s', %s, '%s', '%s', '%s', '%s');")
      update_stmt="UPDATE ip_data SET  update_timestamp=NOW(), total_access=%s, access_times='%s' WHERE ip='%s' AND source='%s';"

      for ip in self.ip_data.keys():
         self.c.execute(check_row % (ip, self.source))
         if self.c.fetchall()[0][0] == 0:
            stmt = insert_stmt % (sorted(self.ip_data[ip]['timestamp'])[0], ip, self.source, len(self.ip_data[ip]['timestamp']),
                                  self._convert_timestamp(sorted(self.ip_data[ip]['timestamp'])), self.ip_data[ip]['coordinates'], 
                                  self.ip_data[ip]['address'], self.ip_data[ip]['places'])
            try:
               self.c.execute(stmt)
            except UnicodeEncodeError:
               pass
         else:
            stmt = update_stmt % (len(self.ip_data[ip]['timestamp']), self._convert_timestamp(sorted(self.ip_data[ip]['timestamp'])), ip, self.source)
            self.c.execute(stmt)

   def _convert_timestamp(self, timestamps:list=[]) -> str:
      """
      Convert a list of timestamps to a string of timestamps
      :args:
         timestamps:list - a list of timestamps
      :return: 
         a string of timestamps
      """
      output='' 
      for timestamp in timestamps:
         output += timestamp +', '
      return output[:-1]
   
   def _send_to_download(self): 
      """
      Send data generated from file into downloads table 
      """
      count_stmt = "SELECT MAX(total_download) FROM downloads WHERE create_timestamp <= NOW();" 
      insert_stmt = "INSERT INTO downloads(create_timestamp, source, repo, daily_download, total_download) VALUES ('%s', '%s', '', %s, %s);" 
      check_stmt = "SELECT COUNT(*) FROM downloads WHERE DATE(create_timestamp) = DATE('%s') AND source='%s';" 

      for timestamp in self.timestamp_data: 
         self.c.execute(count_stmt) 
         total = self.c.fetchall()[0][0] 
         if total is None: 
            total = 0
         self.c.execute(check_stmt % (timestamp, self.source))
         count = self.c.fetchall()[0][0]
         if count == 0: 
            stmt = insert_stmt % (timestamp, self.source, len(self.timestamp_data[timestamp]), len(self.timestamp_data[timestamp])+total)
            self.c.execute(stmt)

   def _send_to_traffic(self):
      """
      Generate data generated from file into traffic table 
      """ 
      count_stmt = "SELECT MAX(total_traffic) FROM traffic WHERE create_timestamp <= NOW();"
      insert_stmt = "INSERT INTO traffic(create_timestamp, source, repo, daily_traffic, total_traffic) VALUES ('%s', '%s', '', %s, %s);"
      check_stmt = "SELECT COUNT(*) FROM traffic WHERE DATE(create_timestamp) = DATE('%s') AND source='%s';"

      for timestamp in self.timestamp_data:
         self.c.execute(count_stmt)
         total = self.c.fetchall()[0][0]
         if total is None:
            total = 0
         self.c.execute(check_stmt % (timestamp, self.source))
         count = self.c.fetchall()[0][0]
         if count == 0:
            stmt = insert_stmt % (timestamp, self.source, len(self.timestamp_data[timestamp]), len(self.timestamp_data[timestamp])+total)
            self.c.execute(stmt)


class GenerateGitHubInfo:
   def __init__(self, cur:pymysql.cursors.Cursor=None, auth=('user@githbu.com', 'pass'), org='NewOrg', repo='NewRepo'): 
      """
      Generate insight regarding clones and traffic for a given GitHub Repo
         self.c:pymysql.cursors.Cursor - MySQL connection cursor 
         self.auth:str                 - GitHub access authentication 
         self.org:str                  - GitHub organization name
         self.repo                     - GitHub repository Name 
      """
      self.c=cur
      self.auth=auth 
      self.org=org 
      self.repo=repo 
      

   def github(self):
      """
      Main class for GenerateGitHubInfo class
      """
      gh = GitHub(auth=self.auth, org=self.org, repo=self.repo)
      self._send_to_traffic(gh.get_traffic())
      self._send_to_download(data=gh.get_clones())  
      self._send_to_github_referral_list(data=gh.get_referral())     

   def _send_to_traffic(self, data:list=[]):
      """
      Send data to traffic 
      """
      print(data) 
      exit(1) 
      insert_stmt = "INSERT INTO traffic(repo, source, daily_traffic, total_traffic) VALUES ('%s', 'GitHub', %s, %s);" 
      count_query = "SELECT MAX(total_traffic) FROM traffic WHERE repo='%s' AND source='GitHub';" 

      stmt = count_query % (repo)
      self.c.execute(stmt)
      total_download = self.c.fetchall()[0][0]
      if total_download is None:
         total_download = 0
      stmt = insert_stmt % (repo, data['uniques'], data['uniques']+total_download)
      self.c.execute(stmt)

   def _send_to_download(self, data:list=[], repo:str='NewRepo'): 
      insert_stmt = "INSERT INTO downloads(repo, source, daily_download, total_download) VALUES ('%s', 'GitHub', %s, %s);" 
      count_query = "SELECT MAX(total_download) FROM downloads WHERE repo='%s' AND source='GitHub';" 

      stmt = count_query % (repo)
      self.c.execute(stmt)
      total_download = self.c.fetchall()[0][0]

      if total_download is None:
         total_download = 0
      stmt = insert_stmt % (repo, data['uniques'], data['uniques']+total_download)
      self.c.execute(stmt)

   def _send_to_github_referral_list(self, data:list=[], repo:str='NewRepo'): 
      insert_stmt = "INSERT INTO github_referral_list(repo, referral, daily_referrals, total_referrals) VALUES ('%s',  '%s', %s, %s);" 
      count_query = "SELECT MAX(total_referrals) FROM github_referral_list WHERE repo='%s' AND referral='%s';" 

      for referral in data:
         stmt = count_query % (repo, referral['referrer']) 
         self.c.execute(stmt) 
         total_referrals = self.c.fetchall()[0][0]
         if total_referrals is None: 
            total_referrals = 0
         stmt = insert_stmt % (repo, referral['referrer'], referral['uniques'], referral['uniques']+total_referrals) 
         self.c.execute(stmt) 





if __name__ == '__main__':
     gi = GenerateInfo()
     gi.main()

     #gib = GenerateIPBasedInfo() 
     #gib.aws_ip()
     #gib.website_ip()
#     ghi = GenerateGitHubInfo()
#     for repo in ["FogLAMP","foglamp-gui","foglamp-pkg","foglamp-snap"]: 
#        ghi.github(auth=('oshadmon@gmail.com', 'OJs071291'), org='foglamp', repo=repo)

