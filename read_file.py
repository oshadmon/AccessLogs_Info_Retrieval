import datetime 
import re 

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
      except ValueError:
         pass
      return timestamp


