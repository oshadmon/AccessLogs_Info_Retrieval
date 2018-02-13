import datetime
import os
import sys
import time

timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d_%H_%M_%S')

file = "merged_file_%s.txt" % str(timestamp)

def main(*args):
   dir = sys.argv[1]
   dir = dir.replace("$HOME", os.getenv("HOME")).replace("$PWD", os.getenv("PWD")).replace("~", os.path.expanduser('~')) 
   new_file = generate_file(dir)
   f = open(new_file,"w")
   print(type(f))
   for file in os.listdir(dir):
      store_line_to_file(dir+"/"+file, f=f) 
   f.close() 

def generate_file(dir:str="") -> str:
   timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d_%H_%M_%S')
   file = "merged_file_%s.txt" % str(timestamp)
   open((dir+"/%s") % file, 'w').close()
   return dir+"/%s" % file 

def store_line_to_file(file:str="", f=None):
   f2 = open(file, 'r')
   for line in f2.readlines():
      f.write(line)
   f2.close()   

if __name__ == '__main__': 
   main()
