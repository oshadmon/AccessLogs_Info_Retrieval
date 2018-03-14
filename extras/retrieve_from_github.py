#!/bin/python3
'''
The following code is based on code written by Niel Chah (nchah) to retrieve statistics from GitHub  
https://github.com/nchah/github-traffic-stats/blob/master/gts/main.py
''' 

import os 
import sys 
from requests import get 

class GitHub: 
   def __init__(self, auth=('user@githbu.com', 'pass'), org=None, repo='NewRepo'):
      """
      Using GitHub connection parameters communicate retrieve insight 
      :args: 
         self.auth:str -  github authentication infromation (user, password)
         self.org:str - organization under whcih repository exists, if no such org tha uses username 
         self.repo:str - repository which insight is relevent to 
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
      Retrive insight regarding traffic 
      :return: 
         dict with information regarding traffic 
      """
      base_url = self.base_url + self.org + '/' + self.repo + '/traffic/views'
      response = get(base_url, auth=self.auth, headers={'Accept': 'application/vnd.github.spiderman-preview'})
      return response.json() 
   
   def get_clones(self) -> dict:
      """
      Retrive insight regarding clone
      :return: 
         dict with information regading clones
      """
      base_url = self.base_url + self.org + '/' + self.repo + '/traffic/clones'
      response = get(base_url, auth=self.auth, headers={'Accept': 'application/vnd.github.spiderman-preview'})
      return response.json() 

   def get_referral(self) -> dict: 
      """
      Retrieve insight regarding referrals 
      :return: 
         dict with information regarding referrals 
      """
      base_url = self.base_url + self.org + '/' + self.repo + '/traffic/popular/referrers'
      response = get(base_url, auth=self.auth, headers={'Accept': 'application/vnd.github.spiderman-preview'})
      return response.json()


