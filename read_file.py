import datetime 
import re 

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
