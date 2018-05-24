import argparse
import psycopg2
import pymysql 

from generate_ip_info     import GenerateIPBasedInfo

def __create_connection(host='127.0.0.1', port=5432, user='root', password='passwd', dbname='test'): 
   """
   Create connection to database
   :params:
      host:str - database host
      port:int - database port
      user:str - database user 
      password:str - database password 
      dbname: str - database name 
   :return:
      open connection to database
   """
   conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname)
   conn.autocommit = True
   return conn.cursor()

def main(): 
   """
   Main to execute generate_ip_info
   :positional arguments:
      host                  host/port connection to database [127.0.0.1:5432]
      user                  user/password to database [root:passwd]
      dbname                database name [test]
      source                Where data is coming from [AWS or Website]
      data_file             File containing data to be sent to database
   :optional arguments:
      -h, --help                  show this help message and exit
   """ 
   parser = argparse.ArgumentParser()
   parser.add_argument('host',      default='127.0.0.1:5432', help='host/port connection to database [127.0.0.1:5432]') 
   parser.add_argument('user',      default='root:passwd',    help='user/password to database [root:passwd]') 
   parser.add_argument('dbname',    default='test',           help='database name [test]')
   parser.add_argument('source',    default='AWS',            help='Where data is coming from [AWS or Website]')  
   parser.add_argument('data_file', default='/tmp/data.txt',  help='File containing data to be sent to database') 
   args = parser.parse_args()

   # create connection
   cur = __create_connection(host=args.host.split(":")[0], port=int(args.host.split(":")[1]), 
                             user=args.user.split(":")[0], password=args.user.split(":")[1], 
                             dbname=args.dbname) 
   # execute script
   gi = GenerateIPBasedInfo(cur=cur, file_name=args.data_file, source=args.source)   
   gi.read_file() 
   gi.send_to_raw_ip() 

if __name__ == '__main__':
   main()


