import sys 
import pymysql 

from generate_ip_info     import GenerateIPBasedInfo
from generate_github_info import GenerateGitHubInfo

class GenerateInfo: 
   def __init__(self, *args): 
      """
      Generate regarding viistors either from file or GitHub
      """
      self._declare_values(values=sys.argv)
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

         # GitHub required config 
         self.auth:str       - GitHub Authentication info 
         self.org:str        - Organization that repo falls under 
         self.repo:str       - Git Repository (if relevent) 
         
         # Non Git config 
         self.file_name:str  - file containing source info  (for non-Git sources)
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
      self.downloads=True
      self.traffic=True

      for value in values: 
         if value is sys.argv[0]: 
            pass 
         if "--host" in value: 
            self.host = str(value.split("=")[-1].split(":")[0])
            self.port = int(value.split("=")[-1].split(":")[1])
         elif "--user" in value: 
            self.user     = str(value.split("=")[-1].split(":")[0])
            self.password = str(value.split("=")[-1].split(":")[1])  
         elif "--db" in value: 
            self.db = str(value.split("=")[-1])
         elif "--source" in value: 
            self.source = str(value.split("=")[-1]) 
         elif "--auth" in value:
            self.auth = "("+str(value.split("=")[-1])+")"
         elif "--org" in value: 
            self.org = str(value.split("=")[-1])
         elif "--repo" in value: 
            self.repo = str(value.split("=")[-1]) 
         elif "--file-name" in value: 
            self.file_name = str(value.split("=")[-1])
         elif "--download" in value: 
            self.traffic = False 
         elif "--traffic" in value: 
            self.downloads = False 
         else: 
            pass  

         if self.org is "NewOrg":
            self.org = self.auth.split("(")[1].split(",")[0].split("@")[0] 
 
   def main(self): 
      if self.source.lower() in ['aws', 'website']: 
         gii = GenerateIPBasedInfo(cur=self.c, file_name=self.file_name, source=self.source) 
         if self.downloads is True: 
            gii.download_ip() 
         if self.traffic is True: 
            gii.traffic_ip() 

      if self.source.lower() is 'github':
         gh = GenerateGitHubInfo(cur=self.c, auth=self.auth, org=self.org, repo=self.repo) 
         gh.github() 
         





if __name__ == '__main__':
     gi = GenerateInfo()
     gi.main()

     #gib = GenerateIPBasedInfo() 
     #gib.aws_ip()
     #gib.website_ip()
#     ghi = GenerateGitHubInfo()
#     for repo in ["FogLAMP","foglamp-gui","foglamp-pkg","foglamp-snap"]: 
#        ghi.github(auth=('oshadmon@gmail.com', 'OJs071291'), org='foglamp', repo=repo)

