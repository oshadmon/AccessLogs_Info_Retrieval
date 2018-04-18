import datetime 
import os
import plotly.offline as offline
import pymysql
import sys 

from plotly.graph_objs import *

class GenerateGraph: 
   def __init__(self, *args): 
      """
      Generate graphs based on the results in database 
      :args: 
         args  (sys.argv):list - Valules declared when calling test (shown in _help method)
      """
      conn = pymysql.connect(host='127.0.0.1', user='root', password='foglamp', db='test', autocommit=True, charset='latin1')
      self.c = conn.cursor()
 
   def _help(self, invalid:str=''):
      """
      Print options to screen and exit
      :args:
         invalid:str - If the user wants an option that isn't supported, then a corresponding error is printed 
      """ 
      if invalid is not "":
         print("Exception - '%s' is not supported\n" % str(invalid))
      print("Option List: "
           +"\n\t--file: location where image is stored [--file=/var/www/html]"
           +"\n\t--title: name of the graph [--title='chart name']" 
           +"\n\t--type: Type of graph (line or hbar) [--type=line]"
           +"\n\t--query: The type of location to check [--query='SELECT * FROM table;']"
           +"\n\t--host: IP address of the PostgresSQL [--host=127.0.0.1]"
           +"\n\t--usr: User and password to connect to postgres [--usr=root:'']"
           +"\n\t--db-name: Name of database being used [--db-name=test]"
           )
      exit(1)

   def create_temp_table(self): 
      """
      Create temporary table from which graphs will be generated 
      """
      create_table=("CREATE TEMPORARY TABLE data("
                   +"xaxy VARCHAR(255) NOT NULL DEFAULT '',"
                   +"daily FLOAT NOT NULL DEFAULT 0.0,"
                   +"total FLOAT NOT NULL DEFAULT 0.0"
                   +");") 
      self.c.execute(create_table)

   def _declare_values(self, values:list=[]): 
      """
      Declare values that are used through the program
      :args:
         file:str - File logs file containing relevent information
         title:str - Name of the graph generated 
         query:str - The type of location to check.
         host:str - IP address of the PostgresSQL
         user:str - User of MySQL 
         dbname:str - database name  
         type:str - type of graph (
      """
      self.file="/var/www/html"
      # self.query = "SELECT * FROM table;"
      self.title = "chart name"
      self.host = '127.0.0.1'
      self.usr = 'root'
      self.passwd = ''
      self.dbname = 'test'
      self.type='line' 

      for value in values:
         if value is sys.argv[0]:
            pass
         elif "--file" in value: 
            self.file = str(value.split("=")[-1])
         elif "--title" in value:
            self.title = str(value.split("=")[-1]) 
         elif "--query" in value:
            self.query = str(value.split("=",1)[-1]) 
         elif "--host" in value:
            self.host = str(value.split("=")[-1])
         elif "--usr" in value:
            self.usr = str(value.split("=")[-1].split(":")[0])
            self.passwd = str(value.split("=")[-1].split(":")[-1])
         elif "--db-name" in value:
            self.dbname = str(value.split("=")[-1])
         elif "--type" in value: 
            self.type = str(value.split("=")[-1])
         else:
            self._help(invalid=value)

   def create_temp_table(self):
      """
      Create temporary table from which graphs will be generated 
      """
      create_table=("CREATE TEMPORARY TABLE data("
                   +"xaxy VARCHAR(255) NOT NULL DEFAULT '',"
                   +"daily FLOAT NOT NULL DEFAULT 0.0,"
                   +"total FLOAT NOT NULL DEFAULT 0.0"
                   +");") 
      self.c.execute(create_table)
   
   def insert_to_temp_table(self): 
      """
      Based on a user defined query, containing 2 rows (1 for x and another for y) generate 
      a table containing the corresponding data, and the sum of y incrementally
      """
      self.query = "SELECT DATE(create_timestamp), SUM(daily_download) FROM downloads WHERE source='AWS' GROUP BY DATE(create_timestamp);" 
      insert = "INSERT INTO data(xaxy, daily, total) VALUES('%s', %s, %s);"
      self.c.execute(self.query) 
      results = self.c.fetchall()
      self.c.execute("SELECT COUNT(*) FROM data") 
      total = 0
      for result in results: 
         total += result[1]
         stmt = insert % (result[0], result[1], total)
         self.c.execute(stmt)

   def _retrieve_data(self) -> dict: 
      """
      Retrieve from data to send to graph 
      :return: 
         dict with data 
      """
      results = []
      i = 0
      self.c.execute("SELECT * FROM data ORDER BY xaxy;") 
      for result in self.c.fetchall():
         results.append(result)
      self.c.close() 
      column={}
      for v in range(len(results[0])):
        column[v]=[]
      for result in results: 
         for key in column.keys(): 
            column[key].append(result[key])
      return column

   def draw_line_graph(self): 
     """
     Based on the results in the table, graph the output
     :args: 
        columns:dict - Dictionary of columns that are being used. 
                       Note that 0 key in columns is the X-axy, all else relate to Y-axy
        layout:Layout - Layout of graph 
        names:list - List of trace names 
     """ 
     xaxy = self.query.split("SELECT")[-1].split(",",1)[0].replace(" ","")
     yaxy = "count" 
     columns = self._retrieve_data() 
     trace_names = ['daily', 'total'] 
     # Generate trace lines
     traces = [] 
     for key in range(1, len(columns)): 
        traces.append(Scatter(x=columns[0], y=columns[key], name=trace_names[key-1])) 
     # Layout 
     layout = Layout( 
           title='Graph 1',
           xaxis=dict(title=xaxy), 
           yaxis=dict(title=yaxy), 
     )
     # Draw 
     data = Data(traces) 
     fig = Figure(data=data, layout=layout)
     offline.plot(fig, filename='/var/www/html/aws.html')
     f = open('/var/www/html/aws.html', 'a') 
     f.write("<body><div><center>"+self.query+"</center></div></body>")

   def main(self):
      """
      Main to generate graphs from data
      """
      self.create_temp_table()
      self.insert_to_temp_table()
      self.draw_line_graph() 
 
if __name__ == '__main__': 
   gg = GenerateGraph()
   gg.main()
