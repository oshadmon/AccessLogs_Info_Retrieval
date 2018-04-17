import requests
import pymysql 
import warnings 

warnings.filterwarnings("ignore")

class GenerateGitHubInfo:
   def __init__(self, cur:pymysql.cursors.Cursor=None, auth=('user@githbu.com', 'pass'), org='NewOrg', repo='NewRepo'):
      """
      Generate insight regarding clones and traffic for a given GitHub Repo
         self.c:pymysql.cursors.Cursor - MySQL connection cursor 
         self.auth:str                 - GitHub access authentication 
         self.org:str                  - GitHub organization name
         self.repo                     - GitHub repository Name 
      """
      self.c=cur
      self.auth=auth
      self.org=org
      self.repo=repo

   def github(self):
      """
      Main class for GenerateGitHubInfo class
      """
      gh = GitHub(auth=self.auth, org=self.org, repo=self.repo)
      self._send_to_traffic(gh.get_traffic())
      self._send_to_download(data=gh.get_clones())
      self._send_to_github_referral_list(data=gh.get_referral())

   def _send_to_traffic(self, data:dict={}):
      """
      Send data to traffic 
      :args: 
         data:dict - traffic insight  
     """
      insert_stmt = "INSERT INTO traffic(repo, source, daily_traffic, total_traffic) VALUES ('%s', 'GitHub', %s, %s);"
      count_query = "SELECT MAX(total_traffic) FROM traffic WHERE repo='%s' AND source='GitHub';"

      self.c.execute(count_query % self.repo)
      total_download = self.c.fetchall()[0][0]
      if total_download is None:
         total_download = 0
      stmt = insert_stmt % (self.repo, data['uniques'], data['uniques']+total_download)
      self.c.execute(stmt)

   def _send_to_download(self, data:dict={}):
      """
      Send data to downloads table 
      :args: 
         data:dict - downloads insight 
      """
      insert_stmt = "INSERT INTO downloads(repo, source, daily_download, total_download) VALUES ('%s', 'GitHub', %s, %s);"
      count_query = "SELECT MAX(total_download) FROM downloads WHERE repo='%s' AND source='GitHub';"

      self.c.execute(count_query % self.repo)
      total_download = self.c.fetchall()[0][0]

      if total_download is None:
         total_download = 0
      stmt = insert_stmt % (self.repo, data['uniques'], data['uniques']+total_download)
      self.c.execute(stmt)

   def _send_to_github_referral_list(self, data:dict={}):
      """
      send data to referral table 
      :args:
         data:dict - github referral insight 
      """
      insert_stmt = "INSERT INTO github_referral_list(repo, referral, daily_referrals) VALUES ('%s',  '%s', %s);"

      for referral in data:
         stmt = insert_stmt % (self.repo, referral['referrer'], referral['uniques'])
         self.c.execute(stmt)

class GitHub:
   def __init__(self, auth=('user@githbu.com', 'pass'), org=None, repo='NewRepo'):
      """
      Using GitHub connection parameters communicate retrieve insight 
      Based on: https://github.com/nchah/github-traffic-stats/blob/master/gts/main.py
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

