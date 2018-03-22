"""
By: Ori Shadmon 
Date: February 2018 
Description: Using a file of IP addresses and TIMESTAMPs generate information in terms of location and potential places. 
""" 

import datetime
import googlemaps
import os
import psycopg2
import re 
import requests
import sys 

from json import dumps 
from pygeocoder import Geocoder

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
      # create connection to db (closed in main when everything is done) 
      conn = psycopg2.connect(host=self.host, user=self.usr, password=self.passwd, dbname=self.dbname)
      conn.autocommit = True
      self.c = conn.cursor()

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
         radius:str - In meters how far from source to check 
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

      self.file = self.file.replace("$HOME", os.getenv("HOME")).replace("$PWD", os.getenv("PWD")).replace("~", os.path.expanduser('~'))
       
   def _sent_to_historical_data(self, data={}, total_access=0, unique_access=0, source=''): 
      """
      Implementation sending data to Postgres database rather print 
      historical_data table is a summary of all the different points where data is coming from 
      :args: 
         data:dict - Relevent data as JSON object 
         total_access:int - Total number access 
         unique_access:int - Number of unique access 
      """
      stmt = "INSERT INTO historical_data(total_access, unique_access, ip_data, from_where) VALUES (%s, %s, '%s', '%s')" 
      stmt = stmt % (total_access, unique_access, dumps(data), source) 
      self.c.execute(stmt)

   def _send_to_ip_data(self, data={}, source='AWS'): 
      """
      Insert into ip_data `ip_data` in details rather than a JSON object 
      :args: 
         data:dict - JSON with data object 
         source:str - where is the original data from 
      """
      check_row="SELECT COUNT(*) FROM ip_data WHERE ip='%s' AND source='%s';" 
      insert_stmt="INSERT INTO ip_data(ip, source, total_access, access_times, coordiantes, address, places) VALUES ('%s', '%s', %s, '%s', '%s', '%s', '%s');"
      update_stmt="UPDATE ip_data SET update_timestamp=NOW(), total_access=%s WHERE ip='%s' AND source='%s';" 

      for ip in data.keys(): 
         self.c.execute(check_row % (ip, source))
         if self.c.fetchall()[0][0] == 0: 
            stmt = insert_stmt % (ip, source, data[ip]['frequency'], data[ip]['timestamp'], data[ip]['coordinates'], data[ip]['address'], data[ip]['places']) 
            self.c.execute(stmt)
         else: 
            stmt = update_stmt % (data[ip]['frequency'], ip, source) 
            self.c.execute(stmt)
 
   def convert_timestamp(self, timestamps=[]) -> str: 
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
   
   def aws_main(self): 
      """
      Retrieve information regarding AWS, send it to database; if valid, print the results
      """
      iff = InfoFromFile(file=self.file) 
      tmp = iff.itterate_file() # Get Information from File
      data = {} 
      total_access=0 

      for ip in tmp: # Get other information
         li = LocationInfo(ip=ip, api_key=self.api_key, query=self.query, radius=self.radius)
         lat, long = li._get_lat_long() 
         coordinates = "(%s, %s)" % (str(lat), str(long))
         address = li._get_address(lat, long)
         places = li._get_possible_places(lat, long, self.query)
         total_access += len(tmp[ip]["timestamp"])
         
         # Store infomration in data 
         data[ip] = {"frequency": len(tmp[ip]["timestamp"]), "timestamp":self.convert_timestamp(tmp[ip]["timestamp"]), "coordinates":coordinates, 
                     "address":address, "places": places} 

 
         # Print to screen 
         if self.stdout is True: 
            if self.timestamp is True: 
               output = "%s -\n\tFrequency: %s\n\tTimestamp: %s\n\tCoordinates: %s\n\tAddress: %s\n\tPlaces: %s"
               print(output % (ip, len(data[ip]["timestamp"]), data[ip]["timestamp"], coordinates, address, places))
            else: 
               output = "%s -\n\tFrequency: %s\n\tCoordinates: %s\n\tAddress: %s\n\tPlaces: %s"
               print(output % (ip, len(data[ip]["timestamp"]), coordinates, address, places))

      # Send to database
      self._sent_to_historical_data(data=data, total_access=total_access, unique_access=len(data.keys()), source='AWS')
      self._send_to_ip_data(data=data, source='AWS')
      self.c.close() 

class InfoFromFile: 
   def __init__(self, file:str="$HOME/tmp/s3_file.txt"): 
      """
      The following class takes a file, and retrieves the IP and access timestamps
      from it. 
      :args: 
         file:str - file containing lines of relevent data
         self.data:dict - Object containing IP (key) and timestamps (value list)
      """    
      self.f = file 
      self.data = {}

   def itterate_file(self)->dict: 
      """
      Itterate through a file containing relevent information
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
      except ValueException:
         return timestamp
      else:
         return timestamp

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
      """
      self.ip = ip
      self.gmaps = googlemaps.Client(key=api_key)
      self.query = query 
      self.radius = radius

   def _get_lat_long(self) -> (float, float): 
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
      lat = 0.0
      long = 0.0
      r = requests.get("https://freegeoip.net/json/" + self.ip)
      json_response = r.json()
      if json_response['latitude'] and json_response['longitude']:
         lat = json_response['latitude']
         long = json_response['longitude']
      return lat, long

   def _get_address(self, lat:float=0.0, long:float=0.0) -> str: 
      """
      Based on the latitude and longitutde, generate address
      :return:
         return address:str
      """
      try: 
         address = self.gmaps.reverse_geocode((lat, long))
      except googlemaps.exceptions._RetriableRequest: 
         return "Failed to get Address due to API Key limit. For more info: https://developers.google.com/maps/documentation/javascript/get-api-key" 
      except googlemaps.exceptions.Timeout: 
         return "Failed to get Address due to API Key timeout. For more info: https://developers.google.com/maps/documentation/javascript/get-api-key"
      else: 
         try:
            return address[0]['formatted_address']
         except:
            return ''

   def _get_possible_places(self, lat:float=0.0, long:float=0.0, query:str="lunch") -> str:
      """
      Generate a list of places based on the lcation, query, and radius (in meters)
      :args: 
         query:str - what the user is searching for
      :return:
         "list" of potential places based on query 
      """
      result = ""
      try: 
         places = self.gmaps.places(query=self.query, location=(lat, long), radius=self.radius)
      except: 
         return "Failed to get potential %s places due to API Key limit. For more info: https://developers.google.com/maps/documentation/javascript/get-api-key" % query
      else: 
         for dict in places['results']:
            result += dict['name'].replace("'","").replace('"',"") + ", "
         return result

if __name__ == "__main__": 
   m = Main() 
   m.aws_main()
