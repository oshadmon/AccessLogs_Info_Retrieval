#!/bin/python3
'''
The following code is based on code written by Niel Chah (nchah) to retrive statistics from GitHub  
https://github.com/nchah/github-traffic-stats/blob/master/gts/main.py
''' 

import os 
import requests 
import sys 

class GitHub: 
   def __init__(self, *args):
      """
      Using GitHub connection parameters communicate retrive insight 
      :args: 
         args  (sys.argv):list - Valules declared when calling test (shown in _help method)
      """
      if "--help" in sys.argv:
         self._help()
      self._declare_values(values=sys.argv)
   
   def _help(self, invalid=''): 
      """
      Print options to screen and exit
      :args: 
         invalid:str - If the user wants an option that isn't supported, then a corresponding error is printed 
      """
      if invalid is not '': 
         print("Exception - '%s' is not supported \n\t" % invalid) 
      print("Option List:"
           +"\n\t--usrpass: state user and password [--usrpass=user@github.com:password]"
           +"\n\t--org: state the orgnization that project is under. [--org=GitHubOrg]"
           +"\n\t\tIf not stated then org becomes the name of the user"  
           +"\n\t--repo: state the repository [--repo=NewRepo]"
      )

   def _declare_values(self, values=[]):
      """
      Declare necessery values
      :args: 
         self.auth:str -  github authentication infromation (user, password)
         self.org:str - organization under whcih repository exists, if no such org tha uses username 
         self.repo:str - repository which insight is relevent to 
         self.base_dir:str - base GitHub URL
      """
      self.auth=(self.user, self.passwd)
      self.org='user'
      self.repo='NewRepo' 
      self.base_url = 'https://api.github.com/repos/'

      for value in values: 
         if (value == sys.argv[0]) or (value == '--help'):
            pass 
         elif "--usrpass" in value: 
            self.auth = (str(value.split("=")[-1].split(":")[0]), str(value.split("=")[-1].split(":")[-1])) 
            if self.org is "user":
               self.org = str(value.split("=")[-1].split(":")[0].split("@")[0])
         elif "--org" in value: 
            self.org = str(value.split("=")[-1])
         elif "--repo" in value: 
            self.repo = str(value.split("=")[-1])
         else: 
            self._help(invalid=value)

   def get_traffic(self) -> dict:
      """
      Retrive insight regarding traffic 
      :return: 
         dict with information regarding traffic 
      """
      base_url = self.base_url + self.org + '/' + self.repo + '/traffic/views'
      response = requests.get(base_url, auth=self.auth, headers={'Accept': 'application/vnd.github.spiderman-preview'})
      return response.json() 
   
   def get_clones(self) -> dict:
      """
      Retrive insight regarding clone
      :return: 
         dict with information regading clones
      """
      base_url = self.base_url + self.org + '/' + self.repo + '/traffic/clones'
      response = requests.get(base_url, auth=self.auth, headers={'Accept': 'application/vnd.github.spiderman-preview'})
      return respons.json() 

