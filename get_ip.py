"""
By: Ori Shadmon 
Date: December 2017 
Description: The following piece of code takes the "Access Log" files from WP Engine, and retirves the following 
- IP Address(es) and how frequently they visited 
- Dates in which they visited 
""" 

import datetime
import re 

class InfoFromFile_WordPress: 
   def __init__(self, line=str): 
      """
      The following class takes a line from WP Engine "Access Logs" and retrives
      both the IP and timestamp from it 
      :args: 
         line:str - a line from WP Engine "Access Logs" 
            66.249.79.52 dianomic.com - [20/Dec/2017:00:21:42 +0000] "GET /robots.txt HTTP/1.1" 200 67 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
      """
      self.line = line 

   def get_ip(self) -> str:
     """
     Retrive IP address from 
     :return: 
        ip - The IP address from the line 
     """  
     IPPattern = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
     return re.findall(IPPattern, self.line)[0]

   def get_timestamp(self) -> datetime.datetime: 
      """
      Get the timestamp from given line (formated dd/mm/yy:hh:mm:ss), and convert it to YY-MM-DD HH:MM:SS) 
      :return:
         timestamp:datetime.datetime - Timestamp when IP accessed website
         If timestamp cannot be formated, then srcipt ignores formating of timestamp
      """ 
      original_date = self.line.split("[")[-1].split("]")[0].split(" +")[0].split(":",1)[0]
      original_time = self.line.split("[")[-1].split("]")[0].split(" +")[0].split(":",1)[-1]
      try: 
         timestamp = datetime.datetime.strptime(original_date, "%d/%b/%Y").strftime("%Y-%m-%d")
      except ValueError: 
         return original_date + " " + original_time 
      else:  
         return(timestamp + " " + original_time) 
     
   def test_info_from_file(self): 
      """
      Test that given a  line, retrives valid information 
      """
      ip = self.get_ip()
      timestamp = self.get_timestamp() 
      try: 
         socket.inet_aton(ip) 
      except socket.error: 
         print("Invalid IP: %s" % ip) 
      else:
         print("Valid IP: %s" % ip )
      try: 
         parse(timestamp)
      except ValueError: 
         print("Invalid Timestamp")
      else:  
         print("Valid Timestamp")

