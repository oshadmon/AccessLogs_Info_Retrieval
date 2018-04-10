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

from github import GitHub 
from location_info import LocationInfo
from read_file import InfoFromFile 

class GenerateIPBasedInfo: 
   def __init__(self): 
      conn = pymysql.connect(host='localhost', user='root', password='foglamp', db='test2', autocommit=True)
      self.c = conn.cursor()

   def aws_ip(self): 
      iff = InfoFromFile(file_name='/home/webinfo/data/output3.txt') 
      self.ip_data, self.timestamp_data = iff.itterate_file() # Get Information from File
      threads=[]
      for ip in self.ip_data: # Get other information
        threads.append(threading.Thread(target=self._generate_location_info, args=(ip,)))
      for t in threads:
         t.start()
      for t in threads:
         t.join()
      self._send_to_ip_data(source='AWS') 
      self._send_to_download() 

   def website_ip(self):
      iff = InfoFromFile(file_name='/home/webinfo/dianomic_apache_logs-2018-03-27_18-12-01.txt')
      self.ip_data, self.timestamp_data = iff.itterate_file() # Get Information from File
      threads=[]
      for ip in self.ip_data: # Get other information
        threads.append(threading.Thread(target=self._generate_location_info, args=(ip,)))
      for t in threads:
         t.start()
      for t in threads:
         t.join()
      self._send_to_ip_data(source='Website')
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

   def _send_to_ip_data(self, source:str='AWS'):
      """
      Insert into ip_data `ip_data` in details rather than a JSON object 
      """
      check_row="SELECT COUNT(*) FROM ip_data WHERE ip='%s' AND source='%s';"
      insert_stmt=("INSERT INTO ip_data(create_timestamp, update_timestamp, ip, source, total_access, access_times, coordiantes, address, places) VALUES " 
                  +"('%s', NOW(), '%s', '%s', %s, '%s', '%s', '%s', '%s');")
      update_stmt="UPDATE ip_data SET  update_timestamp=NOW(), total_access=%s, access_times=%s WHERE ip='%s' AND source='%s';"

      for ip in self.ip_data.keys():
         self.c.execute(check_row % (ip, source))
         if self.c.fetchall()[0][0] == 0:
            stmt = insert_stmt % (sorted(self.ip_data[ip]['timestamp'])[0], ip, source, len(self.ip_data[ip]['timestamp']),
                                  self._convert_timestamp(sorted(self.ip_data[ip]['timestamp'])), self.ip_data[ip]['coordinates'], 
                                  self.ip_data[ip]['address'], self.ip_data[ip]['places'])
            try:
               self.c.execute(stmt)
            except UnicodeEncodeError:
               pass
         else:
            stmt = update_stmt % (len(self.ip_data[ip]['timestamp']), self._convert_timestamp(sorted(self.ip_data[ip]['timestamp'])), ip, 'AWS')
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
      count_stmt = "SELECT MAX(total_download) FROM downloads WHERE create_timestamp <= NOW();" 
      insert_stmt = "INSERT INTO downloads(create_timestamp, source, repo, daily_download, total_download) VALUES ('%s', 'AWS', '', %s, %s);" 
      check_stmt = "SELECT COUNT(*) FROM downloads WHERE DATE(create_timestamp) = DATE('%s') AND source='AWS';" 

      for timestamp in self.timestamp_data: 
         self.c.execute(count_stmt) 
         total = self.c.fetchall()[0][0] 
         if total is None: 
            total = 0
         self.c.execute(check_stmt % timestamp)
         count = self.c.fetchall()[0][0]
         if count == 0: 
            stmt = insert_stmt % (timestamp, len(self.timestamp_data[timestamp]), len(self.timestamp_data[timestamp])+total)
            self.c.execute(stmt)

   def _send_to_traffic(self):
      count_stmt = "SELECT MAX(total_traffic) FROM traffic WHERE create_timestamp <= NOW();"
      insert_stmt = "INSERT INTO traffic(create_timestamp, source, repo, daily_traffic, total_traffic) VALUES ('%s', 'Website', '', %s, %s);"
      check_stmt = "SELECT COUNT(*) FROM downloads WHERE DATE(create_timestamp) = DATE('%s') AND source='Website';"

      for timestamp in self.timestamp_data:
         self.c.execute(count_stmt)
         total = self.c.fetchall()[0][0]
         if total is None:
            total = 0
         self.c.execute(check_stmt % timestamp)
         count = self.c.fetchall()[0][0]
         if count == 0:
            stmt = insert_stmt % (timestamp, len(self.timestamp_data[timestamp]), len(self.timestamp_data[timestamp])+total)
            self.c.execute(stmt)


class GenerateGitHubInfo:
   def __init__(self): 
      conn = pymysql.connect(host='localhost', user='root', password='foglamp', db='test2', autocommit=True)
      self.c = conn.cursor()

   def github(self, auth=('user@githbu.com', 'pass'), org=None, repo='NewRepo'):
      gh = GitHub(auth=auth, org=org, repo=repo)
      self._send_to_traffic(data=gh.get_traffic(), repo=repo)
      self._send_to_download(data=gh.get_clones(), repo=repo)  
      self._send_to_github_referral_list(data=gh.get_referral(), repo=repo)     

   def _send_to_traffic(self, data:list=[], repo:str='NewRepo'):
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
     #gib = GenerateIPBasedInfo() 
     #gib.aws_ip()
     #gib.website_ip()
     ghi = GenerateGitHubInfo()
     for repo in ["FogLAMP","foglamp-gui","foglamp-pkg","foglamp-snap"]: 
        ghi.github(auth=('oshadmon@gmail.com', 'OJs071291'), org='foglamp', repo=repo)

