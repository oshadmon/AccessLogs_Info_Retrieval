"""
Name: Ori Shadmon
Date: February 2018
Description: In cases where a website access logs, work in such a way that each access has its own file, 
             this script merges them into one. 
"""
import datetime
import os
import sys
import time

def main(*args):
   """
   The following controls the entire process
   :args:
      *args (sys.argv) - Expect directory path containg files to be merged
   """
   dir = sys.argv[1]
   dir = dir.replace("$HOME", os.getenv("HOME")).replace("$PWD", os.getenv("PWD")).replace("~", os.path.expanduser('~')) 
   new_file = generate_file(dir)
   f = open(new_file,"w")
   print(type(f))
   for file in os.listdir(dir):
      store_line_to_file(dir+"/"+file, f=f) 
   f.close() 
   print("Merged File: " + new_file)

def generate_file(dir:str="") -> str:
   """
   Generate a new file that will contain the merged lines
   :args:
      dir:str - String containing the path where the merged will be stored
   :return:
      full path and merged file name
   """
   timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d_%H_%M_%S')
   file = "merged_file_%s.txt" % str(timestamp)
   open((dir+"/%s") % file, 'w').close()
   return dir+"/%s" % file 

def store_line_to_file(file:str="", f=None):
   """
   Process that reads each line in file, and pushes it into the new merged file
   :args:
      file:str - File containing lines that need to be merged
      f - File where the merged lines will go
   """
   f2 = open(file, 'r')
   for line in f2.readlines():
      f.write(line)
   f2.close()   

if __name__ == '__main__': 
   main()
