import datetime 
import googlemaps
import pymysql
import re 
import requests
import threading
import warnings

from json import dumps
from pygeocoder import Geocoder

warnings.filterwarnings("ignore")

class GenerateIPBasedInfo: 
   def __init__(self, cur=None, file_name='/tmp/data.txt', source='AWS'): 
      """
      Based on data in file, send corresponding IP and timestamp database
      :param:
         self.cur - database connection 
         self.file_name - file where data is stored 
         self.source - where data is coming from 
      """
      self.cur = cur 
      self.file_name = file_name 
      self.source = source

   def read_file(self): 
      """
      Read data in file, and store IP and timestamps to dictionary 
      :param: 
         self.data - dict containing IPs and timestamps
      """
      self.data = {} 
      f = open(self.file_name, 'r')
      for line in f.readlines():
         ip = self.__get_ip(line)
         if ip in self.data.keys(): 
            self.data[ip].append(self.__get_timestamp(line)) 
         else: 
            self.data[ip] = [self.__get_timestamp(line)] 
      f.close()

   def __get_ip(self, line=''): 
      """
      From line in file get IP address 
      :param: 
         line - line from file that is read 
      """
      IPPattern = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
      return str(re.findall(IPPattern, line)[0])

   def __get_timestamp(self, line=''): 
      """
      From line in file get timestamp 
      :param: 
         line - line from file that is read 
      """
      timestamp = line.split("[")[-1].split("]")[0].split(" +")[0].split(":",1)[0]
      try: 
         timestamp = datetime.datetime.strptime(timestamp, "%d/%b/%Y").strftime("%Y-%m-%d")
      except ValueError:
         pass
      return timestamp 

   def send_to_raw_ip(self): 
      """
      Send data to raw_ip table 

      :table: 
      CREATE TABLE raw_ip_data(
         ip VARCHAR(255) NOT NULL DEFAULT '127.0.0.1',
         source VARCHAR(255) NOT NULL DEFAULT 'AWS',
         access_timestamp TIMESTAMP DEFAULT now()
      );
      """
      check_stmt = "SELECT COUNT(*) FROM raw_ip_data WHERE ip='%s' AND access_timestamp='%s' AND source='%s';" 
      insert_stmt = "INSERT INTO raw_ip_data(ip, access_timestamp, source) VALUES ('%s', '%s', '%s');" 
      for ip in self.data.keys(): 
         for timestamp in self.data[ip]: 
            self.cur.execute(check_stmt % (ip, timestamp, self.source)) 
            if self.cur.fetchall()[0][0] == 0: 
               self.cur.execute(insert_stmt % (ip, timestamp, self.source))


