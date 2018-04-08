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
