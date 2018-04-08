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

from location_info import LocationInfo
from read_file import InfoFromFile 

class GenerateIPBasedInfo: 
   def __init__(self): 
      conn = pymysql.connect(host='localhost', user='root', password='foglamp', db='test2', autocommit=True)
      self.c = conn.cursor()

   def ip(self): 
      iff = InfoFromFile(file_name='/home/webinfo/data/output3.txt') 
      self.data = iff.itterate_file() # Get Information from File
      threads=[]
      for ip in self.data: # Get other information
        threads.append(threading.Thread(target=self._generate_location_info, args=(ip,)))
      for t in threads:
         t.start()
      for t in threads:
         t.join()
      self._send_to_ip_data() 
      self._send_to_download() 

   def _generate_location_info(self, ip:str='127.0.0.1'):
      """
      Commands to generate information about a given IP address 
      :args: 
         ip:str - IP address which is analyzed 
      """
      li = LocationInfo(ip=ip, api_key='AIzaSyA2wFqcg5NG3CiQDIevIVvBmAK-rQxjp8U', query='VC', radius=0)
      self.data[ip]['coordinates'] = li.get_lat_long()
      self.data[ip]['address'] = li.get_address()
      self.data[ip]['places'] = li.get_possible_places()

   def _send_to_ip_data(self):
      """
      Insert into ip_data `ip_data` in details rather than a JSON object 
      """
      self.source='AWS'
      check_row="SELECT COUNT(*) FROM ip_data WHERE ip='%s' AND source='%s';"
      insert_stmt=("INSERT INTO ip_data(create_timestamp, update_timestamp, ip, source, total_access, access_times, coordiantes, address, places) VALUES " 
                  +"('%s', NOW(), '%s', '%s', %s, '%s', '%s', '%s', '%s');")
      update_stmt="UPDATE ip_data SET  update_timestamp=NOW(), total_access=%s, access_times=%s WHERE ip='%s' AND source='%s';"

      for ip in self.data.keys():
         self.c.execute(check_row % (ip, self.source))
         if self.c.fetchall()[0][0] == 0:
            stmt = insert_stmt % (sorted(self.data[ip]['timestamp'])[0], ip, 'AWS', len(self.data[ip]['timestamp']),
                                  self._convert_timestamp(sorted(self.data[ip]['timestamp'])), self.data[ip]['coordinates'], self.data[ip]['address'], self.data[ip]['places'])
            try:
               self.c.execute(stmt)
            except UnicodeEncodeError:
               pass
         else:
            stmt = update_stmt % (len(self.data[ip]['timestamp']), self._convert_timestamp(sorted(self.data[ip]['timestamp'])), ip, 'AWS')
            self.c.execute(stmt)

   def _send_to_download(self): 
      select = "select create_timestamp, SUM(total_access) from ip_data WHERE DATE(update_timestamp) = NOW() group by create_timestamp order by create_timestamp;"
      insert = "INSERT INTO downloads(create_timestamp, source, repo, daily_download, total_download) VALUES ('%s', 'AWS', '', %s, %s)"
      count = "SELECT MAX(total_download) FROM downloads WHERE source='AWS';"

      self.c.execute(select)
      for result in results:
         c.execute(count)
         r = c.fetchall()[0][0] 
         stmt = insert % (result[0], result[1], result[1]+r)
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
   
   def _insert_into_downloads(self): 
   
class GenerateGitHubInfo:
   def __init__(self): 
      conn = pymysql.connect(host='localhost', user='root', password='foglamp', db='test2', autocommit=True)
      self.c = conn.cursor()

   def github(self, auth=('user@githbu.com', 'pass'), org=None, repo='NewRepo'):
      gh = GitHub(auth=auth, org=org, repo=repo)
      self._send_to_traffic(data=gh.get_clones(), repo=repo)
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
     gib = GenerateIPBasedInfo() 
     gib.ip()

