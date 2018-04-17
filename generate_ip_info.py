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
   def __init__(self, cur:pymysql.cursors.Cursor=None, file_name:str='/tmp/output.txt', source='NewSource', 
                api_key='aaabbbcccdddeee1112_123fg',query='lumch', radius=0): 
      """
      The following class uses a files, containing IP and timestamps, to generate insight regarding visitors
      :args: 
         self.c:pymysql.cursors.Cursor - MySQL connection cursor 
         self.file_name:str - file path with data 
         self.source:str - source where data is from (AWS, Website, etc.)
         self.api_key:str - Google Map's API key
         self.query:str - Places that fall under a given category
         self.radius:int - Distance from origin  
      """
      self.c = cur 
      self.file_name = file_name
      self.source=source 
      self.api_key=api_key
      self.query=query
      self.radius=radius 

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
      li = LocationInfo(ip=ip, api_key=self.api_key, query=self.query, radius=self.radius)
      self.ip_data[ip]['coordinates'] = li.get_lat_long()
      self.ip_data[ip]['address'] = li.get_address()
      self.ip_data[ip]['places'] = li.get_possible_places()

   def _send_to_ip_data(self):
      """
      Insert into ip_data `ip_data` in details rather than a JSON object 
      """
      check_row="SELECT COUNT(*) FROM ip_data WHERE ip='%s' AND source='%s';"
      insert_stmt=("INSERT INTO ip_data(create_timestamp, update_timestamp, ip, source, total_access, access_times, coordiantes, address, places) VALUES " 
                  +"('%s', '%s', '%s', '%s', %s, '%s', '%s', '%s', '%s');")

      update_stmt="UPDATE ip_data SET  update_timestamp='%s', total_access=%s, access_times='%s' WHERE ip='%s' AND source='%s';"

      for ip in self.ip_data.keys():
         self.c.execute(check_row % (ip, self.source))
         if self.c.fetchall()[0][0] == 0:
            stmt = insert_stmt % (sorted(self.ip_data[ip]['timestamp'])[0], sorted(self.ip_data[ip]['timestamp'])[-1], ip, self.source, 
                                  len(self.ip_data[ip]['timestamp']), self._convert_timestamp(sorted(self.ip_data[ip]['timestamp'])), 
                                  self.ip_data[ip]['coordinates'], self.ip_data[ip]['address'], self.ip_data[ip]['places'])
            try:
               self.c.execute(stmt)
            except:
               pass
         else:
            stmt = update_stmt % (sorted(self.ip_data[ip]['timestamp'])[-1], len(self.ip_data[ip]['timestamp']), 
                                  self._convert_timestamp(sorted(self.ip_data[ip]['timestamp'])), ip, self.source)
            try: 
               self.c.execute(stmt)
            except: 
               pass 

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
      insert_stmt = "INSERT INTO downloads(create_timestamp, source, repo, daily_download) VALUES ('%s', '%s', '', %s);" 
      check_stmt = "SELECT COUNT(*) FROM downloads WHERE DATE(create_timestamp) = DATE('%s') AND source='%s';" 

      for timestamp in self.timestamp_data: 
         self.c.execute(check_stmt % (timestamp, self.source))
         count = self.c.fetchall()[0][0]
         if count == 0: 
            stmt = insert_stmt % (timestamp, self.source, len(self.timestamp_data[timestamp]))
            self.c.execute(stmt)

   def _send_to_traffic(self):
      """
      Generate data generated from file into traffic table 
      """ 
      insert_stmt = "INSERT INTO traffic(create_timestamp, source, repo, daily_traffic) VALUES ('%s', '%s', '', %s);"
      check_stmt = "SELECT COUNT(*) FROM traffic WHERE DATE(create_timestamp) = DATE('%s') AND source='%s';"

      for timestamp in self.timestamp_data:
         self.c.execute(check_stmt % (timestamp, self.source))
         count = self.c.fetchall()[0][0]
         if count == 0:
            stmt = insert_stmt % (timestamp, self.source, len(self.timestamp_data[timestamp]))
            try: 
               self.c.execute(stmt)
            except: 
               pass


class InfoFromFile:
   def __init__(self, file_name:str="$HOME/tmp/s3_file.txt"):
      """
      The following class takes a file, and retrieves the IP and access timestamps
      from it. 
      :args: 
         file:str - file containing lines of relevent data
      """
      self.f = file_name

   def itterate_file(self)->dict:
      """
      Itterate through a file containing relevent information
      :return:
         ip_data:dict - A dictionary with ip as keys,and timestamps as values 
         timestamp_data:dict - A dictionary with timestamps as keys and ip as values
      """
      f = open(self.f, 'r')
      ip_data = {}
      timestamp_data = {}
      for line in f.readlines():
         ip = self._get_ip(line)
         timestamp = self._get_timestamp(line)
         # iterate by ip and store timestamps into dict 
         if ip not in ip_data:
            ip_data[ip] = {'timestamp':[timestamp]}
         elif timestamp not in ip_data[ip]['timestamp']:
            ip_data[ip]['timestamp'].append(timestamp)

         # iterate by timestamp and store ip into dict 
         if timestamp not in timestamp_data:
            timestamp_data[timestamp] = [ip]
         elif ip not in timestamp_data[timestamp]:
            timestamp_data[timestamp].append(ip)
      f.close()
      return ip_data, timestamp_data

   def _get_ip(self, line:str="")->str:
      """
      Retrieve IP address from line
      :args:
         line containing IP address
      :return: 
         the derived IP address
      """
      IPPattern = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
      return str(re.findall(IPPattern, line)[0])

   def _get_timestamp(self, line:str="")->str:
      """
      Retrieve timestamp from line 
      :args:
         line containing timestamp
      :return:
         the derived timestamp
      """
      timestamp = line.split("[")[-1].split("]")[0].split(" +")[0].split(":",1)[0]
      try:
         timestamp = datetime.datetime.strptime(timestamp, "%d/%b/%Y").strftime("%Y-%m-%d")
      except ValueError:
         pass
      return timestamp


   def _convert_timestamp(self, data:dict={}) -> dict:
      """
      Convert a list of timestamps to a string of timestamps
      :args:
         timestamps:list - a list of timestamps
      :return: 
         a string of timestamps
      """
      for ip in data:
         output = ''
         if len(data[ip]['timestamp']) == 1:
            data[ip]['timestamp'] = data[ip]['timestamp'][0]
         else:
            for timestamp in data[ip]['timestamp']:
               output += str(timestamp)+', '
            data[ip]['timestamp']=output[:-1]
      return data

class LocationInfo:
   def __init__(self, ip:str='127.0.0.1', api_key:str='aaabbbcccdddeee1112_123fg', query:str='lunch', radius:int=0):
      """
      The following class, takes an IP address, and then using Google's API generates a rough calculation of which
      places accessed the site. This is done using a query (specify the type of location), and radius (how far from the
      source should the system check). Note that the radius is in Meters. 
      :args: 
         ip:str - the IP address that accessed the site
         gmaps:str - Google's API key to use Google Maps API (https://developers.google.com/maps/documentation/javascript/get-api-key)
         query: str - The type of location to check. 
         radius:int - In meters how far from source to check  
         api_key:str - Google's Maps API key 
      """
      self.ip = ip
      self.gmaps = googlemaps.Client(key=api_key)
      self.query = query
      self.radius = radius
      self.api_key=api_key

   def get_lat_long(self) -> str:
      """
      This function connects to the FreeGeoIP web service to get info from IP addresses.
      Returns two latitude and longitude.
      Code from: https://github.com/pieqq/PyGeoIpMap/blob/master/pygeoipmap.py
      :args:
         long:float - correspnds to the longitutude
         lat:float - corresponds to the latitude 
      :return:
         Return the address and lat/long of each IP accesseing dianomic
         if there is an error then code returns lat/long
      """
      self.lat = 0.0
      self.long = 0.0
      r = requests.get("https://freegeoip.net/json/" + self.ip)
      json_response = r.json()
      if json_response['latitude'] and json_response['longitude']:
         self.lat = json_response['latitude']
         self.long = json_response['longitude']
      return "("+str(self.lat)+","+str(self.long)+")"

   def get_address(self):
      """
      Based on the latitude and longitutde, generate address
      :return:
         return address:str
      """
      try:
         address = self.gmaps.reverse_geocode((self.lat, self.long))
      except googlemaps.exceptions._RetriableRequest:
         return "Failed to get Address due to API Key limit. For more info: https://developers.google.com/maps/documentation/javascript/get-api-key"
      except googlemaps.exceptions.Timeout:
         return "Failed to get Address due to API Key timeout. For more info: https://developers.google.com/maps/documentation/javascript/get-api-key"
      else:
         try:
            return str(address[0]['formatted_address']).replace("'","").replace('"','')
         except:
            return ''

   def get_possible_places(self) -> str:
      """
      Generate a list of places based on the lcation, query, and radius (in meters)
      :args: 
      :return:
         "list" of potential places based on query 
      """
      result = ""
      try:
         places = self.gmaps.places(query=self.query, location=(self.lat, self.long), radius=self.radius)
      except:
         return "Failed to get potential %s places due to API Key limit. For more info: https://developers.google.com/maps/documentation/javascript/get-api-key" % self.query
      else:
         for dict in places['results']:
            result += dict['name'].replace("'","").replace('"',"") + ", "
         return result[:-2]
