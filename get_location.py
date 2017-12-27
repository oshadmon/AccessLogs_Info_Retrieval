"""
By: Ori Shadmon
Date: December 2017
Description: Based on the IP address, the code usese pygecoder and googlemaps to find both location and near place places
"""


import googlemaps
from pygeocoder import Geocoder
import requests

class  InfoFromIP: 
   def __init__(self, ip='127.0.0.1', api_key='aaabbbcccdddeee1112_123fg-aS4', query='lunch', radius=0): 
     """
     Initiate the class 
     :args: 
        ip:str - IP address 
        self.api_key:str - Google API Key (https://developers.google.com/maps/documentation/javascript/get-api-key) 
        self.query:str - Query to find near by address 
        self.radius:int - distance from IP address in meters 
        self.lat:float, self.long:float - latitude and longitutde coordinates 
     """
     self.api_key = api_key
     self.query = query 
     self.radius = radius 
     self.lat, self.long = self._get_lat_long(ip=ip)   
   
   def _get_lat_long(self, ip='127.0.0.1') -> (float, float):
      """
      This function connects to the FreeGeoIP web service to get info from IP addresses.
      Returns two latitude and longitude.
      Code from: https://github.com/pieqq/PyGeoIpMap/blob/master/pygeoipmap.py
      :return:
         Return the address and lat/long of each IP accesseing dianomic
         if there is an error then code returns lat/long
      """
      lat = 0.0 
      long = 0.0
      r = requests.get("https://freegeoip.net/json/" + ip)
      json_response = r.json()
      if json_response['latitude'] and json_response['longitude']:
         lat = json_response['latitude']
         long = json_response['longitude'] 
      return lat, long

   def return_lat_long_values(self) -> (float, float): 
      """
      Return longitutde and latitude
      :return: 
         latitude (float) and longitutde (float) 
      """
      return self.lat, self.long

   def get_address(self) -> str:  
      """
      Based on the latitude and longitutde, generate address
      :return:
         return address:str
      """  
      gmaps = googlemaps.Client(key=self.api_key)
      address = gmaps.reverse_geocode((self.lat, self.long)) 
      return address[0]['formatted_address']

   def get_possible_owners(self) -> list:
      """
      Generate a list of places based on the lcation, query, and radius (in meters)
      :return:
         list of query based results
      """
      result = []
      gmaps = googlemaps.Client(key=self.api_key)
      places = gmaps.places(query=self.query, location=(self.lat, self.long), radius=self.radius) 
      for dict in places['results']: 
         result.append(dict['name'])
      return result
