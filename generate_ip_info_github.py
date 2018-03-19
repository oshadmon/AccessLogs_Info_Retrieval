"""
By: Ori Shadmon 
Date: February 2018 
Description: The following script generates information regarding GitHub  
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
      """The following class controls the processes by which everything runs
      :args: 
         args  (sys.argv):list - Valules declared when calling test (shown in _help method)
      """
      if "--help" in sys.argv: 
         self._help()
      self._declare_values(values=sys.argv)

   def _help(self, invalid:str=""):
      """Print options to screen and exit
      :args: 
         invalid:str - If the user wants an option that isn't supported, then a corresponding error is printed 
      """ 
      if invalid is not "":
         print("Exception - '%s' is not supported\n" % str(invalid))
      print("Option List: "
           +"\n\t--host: IP address of the PostgresSQL [--host=127.0.0.1]"
           +"\n\t--usr: User and password to connect to postgres [--usr=root:'']"
           +"\n\t--db-name: Name of database being used [--db-name=test]"  
           +"\n\t--git-usr: Usernamne and password to access git [--git-usr='user@github.com':'password']"
           +"\n\t--git-org: Organization under which repository exists [--git-org='user']"
           +"\n\t--git-repo: Repository name [--git-repo=NewRepo]"
           +"\n\t--stdout: print to screen otherwise will just store to database (default false)"
           ) 
      exit(1)

   def _declare_values(self, values:list=[]): 
      """Declare values that are used through the program
      :args:
         host:str - IP address of the PostgresSQL
         user:str - User of the PostgresSQL  
         pass:string - password of PostgresSQL user 
         dbname:str - database name  
         stdout:boolean - Print output to screen 
         auth:str - github authentication ('user@github.com', 'password') 
         org:str -  organization name 
         repo:str - Repository name 
      """
      self.host = '127.0.0.1' 
      self.usr = 'root' 
      self.passwd = '' 
      self.dbname = 'test' 
      self.stdout = False
      
      # GitHub requirments 
      self.auth=('user@github.com', 'password')
      self.org=None 
      self.repo=[]

      for value in values: 
         if value is sys.argv[0]: 
            pass 
         elif "--host" in value: 
            self.host = str(value.split("=")[-1]) 
         elif "--usr" in value: 
            self.usr = str(value.split("=")[-1].split(":")[0]) 
            self.passwd = str(value.split("=")[-1].split(":")[-1]) 
         elif "--db-name" in value:
            self.dbname = str(value.split("=")[-1]) 
         elif "--stdout" in value: 
            self.stdout = True 
         elif "--git-usr" in value: 
            self.auth = (str(value.split("=")[-1].split(":")[0]), str(value.split("=")[-1].split(":")[-1])) 
         elif "--git-org" in value: 
            self.org = str(value.split("=")[-1]) 
         elif "--git-repo" in value: 
            for value in value.split("=")[-1].split(","):
               self.repo.append(value.replace(" ", ""))
         else: 
            self._help(invalid=value)
       
   def _sent_to_historical_data(self, data={}, total_access=0, unique_access=0, source=''): 
      """Implementation sending data to Postgres database rather print 
      :args: 
         ip:str - IP address 
         frequency:int - how instances of the IP there are 
         timestamp:list - A list (as string) of timestamp 
         coordinates:list - coordiantes from which IP was accessed 
         address:str - address of ip 
         places:str - potential list of places 
      """
      stmt = "INSERT INTO historical_data(total_access, unique_access, ip_info, from_where) VALUES (%s, %s, '%s', '%s')" 
      stmt = stmt % (total_access, unique_access, dumps(data), source) 
      conn = psycopg2.connect(host=self.host, user=self.usr, password=self.passwd, dbname=self.dbname)
      conn.autocommit = True 
      c = conn.cursor() 
      c.execute(stmt)
      c.close() 

   def _send_to_github_data(self, repo='', data={}): 
      inst_stmt = "INSERT INTO github_data(repo, info, total, uniques) VALUES ('%s', '%s', %s, %s);" 
      conn = psycopg2.connect(host=self.host, user=self.usr, password=self.passwd, dbname=self.dbname)
      conn.autocommit = True
      c = conn.cursor()
      for key in data.keys(): 
         stmt= inst_stmt % (repo, key, data[key]['count'], data[key]['unique']) 
         c.execute(stmt)
      c.close() 

   def _send_to_github_referral_list(self, data={}): 
      check_count="SELECT COUNT(*) FROM github_referral_list WHERE referrer='%s';" 
      insert_stmt="INSERT INTO github_referral_list(referrer, unique_referrals, count_referrals) VALUES ('%s', %s, %s)" 
      update_stmt="UPDATE github_referral_list SET unique_referrals=%s, count_referrals=%s WHERE referrer='%s'" 

      conn = psycopg2.connect(host=self.host, user=self.usr, password=self.passwd, dbname=self.dbname)
      conn.autocommit = True
      c = conn.cursor()
 
      for value in data: 
         c.execute(check_count % value['referrer'])
         if c.fetchall()[0][0] == 0:
            stmt = insert_stmt % (value['referrer'], value['uniques'], value['count'])
            c.execute(stmt)
         else: 
            stmt = update_stmt % (value['uniques'], value['count'], value['referrer']) 
            c.execute(stmt)
      c.close() 

   def github_main(self): 
      """
      Retrieve information regarding GitHub, and send it to database
      If valid, print relevent information
      """
      for repo in self.repo: 
         gh=GitHub(auth=self.auth, org=self.org, repo=repo) 
         tmp={"traffic": gh.get_traffic(), "clones": gh.get_clones(), "referral": gh.get_referral()}
         self._send_to_github_referral_list(data=tmp['referral'])

         data={'referral':{'count':tmp['referral'][0]['count'], 'unique':tmp['referral'][0]['uniques'], 'refferer':tmp['referral'][0]['referrer']},
               'clones':{'count':tmp['clones']['count'], 'unique':tmp['clones']['uniques']}, 'traffic':{'count':tmp['traffic']['count'], 'unique':tmp['traffic']['uniques']}}

         self._sent_to_historical_data(data=data, total_access=data['clones']['count'], unique_access=data['clones']['unique'], source='GitHub') 
         self._send_to_github_data(repo=repo, data=data) 
         self._send_to_github_referral_list(data=tmp['referral']) 

         if self.stdout is True: 
            stmt="\nClones - \n\tTotal: %s | Unique: %s\nTraffic -\n\tTotal: %s | Unique: %s\nReferreral - \n\tTotal: %s | Unique: %s | Origin: %s" 
            stmt = stmt % (data['clones']['count'], data['clones']['unique'], 
                       data['traffic']['count'], data['traffic']['unique'], 
                       data['referral']['count'], data['referral']['unique'], tmp['referral'][0]['referrer'])
            print(stmt) 

class GitHub:
   def __init__(self, auth=('user@githbu.com', 'pass'), org=None, repo='NewRepo'):
      """
      Using GitHub connection parameters communicate retrieve insight 
      :args: 
         self.auth:str -  github authentication information (user, password)
         self.org:str - organization under which repository exists, if no such org then uses username 
         self.repo:str - repository which insight is relevant to 
         self.base_dir:str - base GitHub URL
      """
      self.auth = auth
      if org is None:
         self.org=str(self.auth).split("('")[-1].split("@")[0]
      else:
         self.org = org
      self.repo = repo
      self.base_url = 'https://api.github.com/repos/'

   def get_traffic(self) -> dict:
      """
      Retrieve insight regarding traffic 
      :return: 
         dict with information regarding traffic 
      """
      base_url = self.base_url + self.org + '/' + self.repo + '/traffic/views'
      response = requests.get(base_url, auth=self.auth, headers={'Accept': 'application/vnd.github.spiderman-preview'})
      return response.json()

   def get_clones(self) -> dict:
      """
      Retrieve insight regarding clone
      :return: 
         dict with information regading clones
      """
      base_url = self.base_url + self.org + '/' + self.repo + '/traffic/clones'
      response = requests.get(base_url, auth=self.auth, headers={'Accept': 'application/vnd.github.spiderman-preview'})
      return response.json()

   def get_referral(self) -> dict:
      """
      Retrieve insight regarding referrals 
      :return: 
         dict with information regarding referrals 
      """
      base_url = self.base_url + self.org + '/' + self.repo + '/traffic/popular/referrers'
      response = requests.get(base_url, auth=self.auth, headers={'Accept': 'application/vnd.github.spiderman-preview'})
      return response.json()


if __name__ == "__main__": 
   m = Main() 
   m.github_main()
