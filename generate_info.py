import psycopg2
import pymysql 
import sys 

from generate_ip_info     import GenerateIPBasedInfo
from generate_github_info import GenerateGitHubInfo

class GenerateInfo: 
   def __init__(self, *args): 
      """
      Generate regarding viistors either from file or GitHub
      """
      if "--help" in sys.argv: 
         self._help()
      self._declare_values(values=sys.argv)
      if self.psql is True: 
         conn = psycopg2.connect(host=self.host, port=self.port, user=self.user, password=self.password, dbname=self.db) 
         conn.autocommit = True
         self.c.cursor() 
      else: 
         conn = pymysql.connect(host=self.host, port=self.port,  user=self.user, password=self.password, db=self.db, autocommit=True)
         self.c = conn.cursor()

   def _declare_values(self, values:list=[]): 
      """
      Based on user input set variables 
      :args: 
         # database config & "generic" config  
         self.host:str       - database host 
         self.port:int       - database port  
         self.user:str       - database user 
         self.passwd:str     - database password 
         self.db:str         - database name 
         self.source:str     - source from which data is derived 
         self.psql: bool     - write to postgres instead of MySQL 

         # GitHub required config 
         self.auth:str       - GitHub Authentication info 
         self.org:str        - Organization that repo falls under 
         self.repo:str       - Git Repository (if relevent) 
         
         # None Git config 
         self.file_name:str  - file containing source info  (for non-Git sources)
         self.api_key:str    - Google API Key
         self.query:str      - Category which location falls under (such as lunch)
         self.radius:int     - How far from origin to find locations
         self.downloads:bool - only store download results 
         self.traffic:bool   - only store traffic results   
         
         Note if neither downloads or traffic is set, then execute both 
      """
      self.host='localhost' 
      self.port=3306 
      self.user='root' 
      self.password=''
      self.db='test'
      self.source='NewSource'
      self.auth="('user@githbu.com', 'pass')" # GitHub user and password info code (if statement adds parentheses)  
      self.org='NewOrg' # GitHub repository (if set to 'NewOrg' then uses GitHub user instead)  
      self.repo='NewRepo' # Git Repository 
      self.file_name='/tmp/output.txt' # For none Git sources  
      self.api_key='AAABBBCCCDDD1234'
      self.query='lunch' 
      self.radius=0 
      self.downloads=True
      self.traffic=True
      self.psql=False

      for value in values: 
         if value is sys.argv[0]: 
            pass 
         elif "--host" in value.lower(): 
            self.host = str(value.split("=")[-1].split(":")[0])
            self.port = int(value.split("=")[-1].split(":")[1])
         elif "--user" in value.lower(): 
            self.user     = str(value.split("=")[-1].split(":")[0])
            self.password = str(value.split("=")[-1].split(":")[1])  
         elif "--db" in value.lower(): 
            self.db = str(value.split("=")[-1])
         elif "--source" in value.lower(): 
            self.source = str(value.split("=")[-1]) 
         elif "--git-auth" in value.lower():
            self.auth = (str(value.split("=")[-1].split(":")[0]), str(value.split("=")[-1].split(":")[-1]))
         elif "--org" in value.lower(): 
            self.org = str(value.split("=")[-1])
         elif "--repo" in value.lower(): 
            self.repo = str(value.split("=")[-1]) 
         elif "--file-name" in value.lower(): 
            self.file_name = str(value.split("=")[-1])
         elif "--download" in value.lower(): 
            self.traffic = False 
         elif "--traffic" in value.lower(): 
            self.downloads = False 
         elif "--psql" in value.lower(): 
            self.psql = True
         elif "--api-key" in value.lower(): 
            self.api_key = str(value.split("=")[-1])
         elif "--query" in value.lower(): 
            self.query = str(value.split("=")[-1])
         elif "--radius" in value.lower(): 
            self.radius = int(value.split("=")[-1]) 
         else: 
            self._help(value=value) 
         # If user doesn't specify org, then use authentication username 
         if self.org is "NewOrg":
            self.org = self.auth.split("(")[1].split(",")[0].split("@")[0] 

   def _help(self, value:str=None): 
      """
      Generate output with info about requirments
      :arg:
         value:str - invalid value  
      """
      if value is not None: 
         print("%s - Invalid variable" % value) 
      print("Options:"
           +"\n\t--host: database host and port           [--host=127.0.0.1:3306]"
           +"\n\t--user: database user and password       [--user=root:passwd]" 
           +"\n\t--db:   database name                    [--db=test] " 
           +"\n\t--source: Where the data is coming from  [--source=NewSource]" 
           +"\n\t--psql: use PostgresSQL instead of MySQL " 
           +"\n\nGitHub Requirements" 
           +"\n\t--git-auth: GitHub authentication information                                 [--git-auth='user@githbu.com':'password']"
           +"\n\t--org: Organization that repo falls under (if none then uses GitHub username) [--org=NewOrg]" 
           +"\n\t--repo: GitHub Repository Name                                                [--repo=NewRepo]"
           +"\n\nFile based insight" 
           +"\n\t--fine-name: file name and path with insight                                  [--file-name=$HOME/tmp.txt]" 
           +"\n\t--api-key: Google's API Key                                                   [--api-key=AAABBBCCC-123]" 
           +"\n\t--query: Category location falls under                                        [--query='lunch spot']"
           +"\n\t--radius: Distance from origin                                                [--radius=0]" 
           +"\n\t--downloads: Write only to downloads table (false by default)"  
           +"\n\t--traffic: Write only to traffic table (false by default)"
           ) 
      exit(1) 

   def main(self): 
      if self.source.lower() in ['aws', 'website']: 
         gii = GenerateIPBasedInfo(cur=self.c, file_name=self.file_name, source=self.source, api=self.api_key, query=self.query, radius=self.radius) 
         if self.downloads is True: 
            gii.download_ip() 
         if self.traffic is True: 
            gii.traffic_ip() 

      if self.source.lower() == 'github':
         gh = GenerateGitHubInfo(cur=self.c, auth=self.auth, org=self.org, repo=self.repo) 
         gh.github() 
         





if __name__ == '__main__':
     gi = GenerateInfo()
     gi.main()


