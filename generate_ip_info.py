"""
By: Ori Shadmon 
Date: February 2018 
Description: The following piece of code takes the "Access Log" file and retirves the IP Addresses, and access dates. 
It then usees the IP Addresses, and uses Google Maps and https://freegeoip.net/ to get location and its corresponding
information.  
""" 

import datetime
import googlemaps
import os
import psycopg2
from pygeocoder import Geocoder
import re 
import requests
import sys 

class Main: 
   def __init__(self, *args): 
      """
      The following class controls the processes by which everything runs
      :args: 
         args  (sys.argv):list - Valules declared when calling test (shown in _help method)
      """
      if "--help" in sys.argv: 
         self._help()
      self._declare_values(values=sys.argv)

   def _help(self, invalid:str=""):
      """
      Print options to screen and exit
      :args: 
         invalid:str - If the user wants an option that isn't supported, then a corresponding error is printed 
      """ 
      if invalid is not "":
         print("Exception - '%s' is not supported\n" % str(invalid))
      print("Option List: "
           +"\n\t--file: log file containing relevent information [--file=$HOME/tmp/site_logs.txt]"
           +"\n\t--api-key: Google's API key to use Google Maps API [--api-key=aaaBcD123kd-d83c-C83s]"
           +"\n\t--query: The type of location to check [--query=lunch]"
           +"\n\t--radius: In meters how far from source to check [--radius=0]"
           +"\n\t--timestamp:  Print a list the accessed timestamps per IP. If set to False (default), then print only the number of times that IP accessed the website"
           +"\n\t--stdout: print to screen otherwise will just store to database (default false)" 
           +"\n\t--host: IP address of the PostgresSQL [--host=127.0.0.1]"
           +"\n\t--usr: User and password to connect to postgres [--usr=root:'']"
           +"\n\t--db-name: Name of database being used [--db-name=test]"  
           ) 
      exit(1)

   def _declare_values(self, values:list=[]): 
      """
      Declare values that are used through the program
      :args:
         file:str - File logs file containing relevent information
         api_key:str - Google's API key to use Google Maps API (https://developers.google.com/maps/documentation/javascript/get-api-key)
         query:str - The type of location to check.
         radius:int - In meters how far from source to check 
         timestamp:boolean - Return a list the accessed timestamps per IP. If set to False (default), then print only the number of times
	                     that IP accessed the website
         host:str - IP address of the PostgresSQL
         user:str - User of the PostgresSQL  
         pass:string - password of PostgresSQL user 
         dbname:str - database name  
         stdout:boolean - Print output to screen 
      """
      self.file = "$HOME/tmp/site_logs.txt"
      self.api_key = "aaaBcD123kd-d83c-C83s" # The API Key is invalid, user must include a valid IP for code to work
      self.query = "lunch" 
      self.radius = 0
      self.timestamp = False
      self.host = '127.0.0.1' 
      self.usr = 'root' 
      self.passwd = '' 
      self.dbname = 'test' 
      self.stdout = False

      # Based on command line args set corresponding values 
      for value in values: 
         if value is sys.argv[0]: 
            pass 
         elif "--file" in value: 
            self.file = value.split("=")[-1]
         elif "--api-key" in value: 
            self.api_key = value.split("=")[-1]
         elif "--query" in value: 
            self.query = value.split("=")[-1]
         elif "--radius" in value: 
            self.radius = int(value.split("=")[-1]) 
         elif "--timestamp" in value: 
            self.timestamp = True
         elif "--host" in value: 
            self.host = str(value.split("=")[-1]) 
         elif "--usr" in value: 
            self.usr = str(value.split("=")[-1].split(":")[0]) 
            self.passwd = str(value.split("=")[-1].split(":")[-1]) 
         elif "--db-name" in value:
            self.dbname = str(value.split("=")[-1]) 
         elif "--stdout" in value: 
            self.stdout = True 
         else: 
            self._help(invalid=value)
      
      # For cases where command line arg uses ~/ or $HOME/ convert to full path 
      self.file = self.file.replace("$HOME", os.getenv("HOME")).replace("$PWD", os.getenv("PWD")).replace("~", os.path.expanduser('~'))
       
   def _sent_to_historical_data(self, data={}): 
      """
      Implementation sending data to Postgres database rather print 
      :args: 
         data:dir - dictionary with information 
      """
      # Total accessed is the sum of all frequencies 
      total_access = 0
      for ip in data.keys(): 
         total_access += data[ip]["frequency"]
      
      # Insert relevent information into database.
      stmt = "INSERT INTO historical_data(total_access, unique_access, ip_info) VALUES (%s, %s, '%s')" 
      stmt = stmt % (total_access, len(data.keys()), data) 
      stmt = stmt.replace("'",'"').replace('"{',"'{").replace('}"', "}'").replace("AWS",'AWS')
      conn = psycopg2.connect(host=self.host, user=self.usr, password=self.passwd, dbname=self.dbname)
      conn.autocommit = True 
      c = conn.cursor() 
      c.execute(stmt)
      c.close() 
   
   def _convert_timestamp(self, timestamps=[]) -> str: 
      """
      Convert a list of timestamps to a string of timestamps
      :args:
         timestamps:list - a list of timestamps
      :return: 
         a string of timestamps
      """
      output = "" 
      for timestamp in timestamps: 
            output += str(timestamp) +", "
      return output
   
   def main(self): 
      """
      Main process for script
      """
      iff = InfoFromFile(file_name=self.file) 
      tmp = iff.itterate_file() # Get Information from File
      data = {} 
      for ip in tmp: 
         # Retrive and format information that should be stored per IP 
         li = LocationInfo(ip=ip, api_key=self.api_key, query=self.query, radius=self.radius)
         coordinates = li.get_lat_long()
         address = li._get_address()
         places = li._get_possible_places()
         timestamps = self._convert_timestamp(timestamps=tmp[ip]["timestamp"])
         
         # In data dict store a dict with relevent infromation where IP are keys 
         data[ip] = {"frequency": len(tmp[ip]["timestamp"]), "timestamp":timestamps, "coordinates":coordinates, "address":address, "places": places} 

         # Print to screen 
         if self.stdout is True: 
            if self.timestamp is True: 
               output = "%s -\n\tFrequency: %s\n\tTimestamp: %s\n\tCoordinates: %s\n\tAddress: %s\n\tPlaces: %s"
               print(output % (ip, len(data[ip]["timestamp"]), data[ip]["timestamp"], coordinates, address, places))
            else: 
               output = "%s -\n\tFrequency: %s\n\tCoordinates: %s\n\tAddress: %s\n\tPlaces: %s"
               print(output % (ip, len(data[ip]["timestamp"]), coordinates, address, places))


      # Send to database
      self._sent_to_historical_data(data=data)

class InfoFromFile: 
   def __init__(self, file_name:str="$HOME/tmp/s3_file.txt"): 
      """
      The following class takes a file, and retrives the IP and access timestamps
      from it. 
      :args: 
         file:str - file containing lines of relevent data
         self.data:dict - Object containing IP (key) and timestamps (value list)
      """    
      self.f = file_name 
      self.data = {}

   def itterate_file(self)->dict: 
      """
       Main method of the class which results in a generated dictionary of IPs (key) and timestamps list (values) 
      :return:
         return dict containing IPs and their corresponding timestamps
      """
      f = open(self.f, 'r')
      for line in f.readlines(): 
         ip = self._get_ip(line)
         timestamp = self._get_timestamp(line)
         if ip in self.data and timestamp not in self.data[ip]: 
            if timestamp not in self.data[ip]["timestamp"]: 
               self.data[ip]["timestamp"].append(timestamp)
         elif ip not in self.data: 
            self.data[ip]={"timestamp":[timestamp]}
      f.close()
      return self.data 

   def _get_ip(self, line:str="")->str: 
      """
      Retrive IP address from line
      :args:
         line containing IP address
      :return: 
         the derived IP address
      """
      IPPattern = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
      return re.findall(IPPattern, line)[0]

   def _get_timestamp(self, line:str="")->str:
      """
      Retrive timestamp from line 
      :args:
         line containing timestamp
      :return:
         the derived timestamp
      """
      timestamp = line.split("[")[-1].split("]")[0].split(" +")[0].split(":",1)[0]
      try:
         timestamp = datetime.datetime.strptime(timestamp, "%d/%b/%Y").strftime("%Y-%m-%d")
      except ValueException:
         return timestamp
      else:
         return timestamp

class LocationInfo: 
   def __init__(self, ip:str='127.0.0.1', api_key:str='aaabbbcccdddeee1112_123fg', query:str='lunch', radius:int=0): 
      """
      The following class takes an IP and generates information regarding location (coordinates and address), as well as 
      a list of potential sources; based on a user defined query. 
      :args: 
         ip:str - the IP address that accessed the site
         gmaps:str - Google's API key to use Google Maps API (https://developers.google.com/maps/documentation/javascript/get-api-key)
         query: str - The type of location to check. 
         radius:int - In meters how far from source to check  
      """
      self.ip = ip
      self.gmaps = googlemaps.Client(key=api_key)
      self.query = query 
      self.radius = radius
      # default values for latitude and longitude 
      self.lat = 0.0
      self.long = 0.0


   def get_lat_long(self)->str: 
      """
      Using FreeGeoIP web service, generate cooredinates (lat, and long) based on an IP address.        
      :source:
         https://github.com/pieqq/PyGeoIpMap/blob/master/pygeoipmap.py
      :return:
         (latitude, longitude)
      """
      r = requests.get("https://freegeoip.net/json/" + self.ip)
      json_response = r.json()
      if json_response['latitude'] and json_response['longitude']:
         self.at = json_response['latitude']
         self.long = json_response['longitude']
      return "(%s, %s)" % (str(self.lat), str(self.long))

   def _get_address(self) -> str: 
      """
      Based on the latitude and longitude generate location address
         lat:float - latitude 
         lon:float - longitude 
      :return:
         return location address
      """
      try: 
         address = self.gmaps.reverse_geocode((self.lat, self.long))
      except googlemaps.exceptions._RetriableRequest: 
         return "Failed to get Address due to API Key limit. For more info: https://developers.google.com/maps/documentation/javascript/get-api-key" 
      except googlemaps.exceptions.Timeout: 
         return "Failed to get Address due to API Key timeout. For more info: https://developers.google.com/maps/documentation/javascript/get-api-key"
      else: 
         try:
            return address[0]['formatted_address']
         except:
            return ''

   def _get_possible_places(self) -> str:
      """
      Generate a list of places based on the lcation, query, and radius (in meters)
      :args: 
      :return:
         "list" of potential places based on query 
      """
      result = ""
      try: 
         places = self.gmaps.places(query=self.query, location=(self.lat, self.long), radius=self.radius)
      except googlemaps.exceptions as e: 
         return "Failed to get potential %s places due to API Key limit. For more info: https://developers.google.com/maps/documentation/javascript/get-api-key" % query
      except ooglemaps.exceptions.Timeout:
         return "Failed to get potential %s places due to API Key timeout. For more info: https://developers.google.com/maps/documentation/javascript/get-api-key" % query 
      else: 
         for dict in places['results']:
            result += dict['name'].replace("'","").replace('"',"") + ", "
         return result


if __name__ == "__main__": 
   m = Main() 
   m.main()
