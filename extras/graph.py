import datetime 
import os
import plotly.offline as offline
import psycopg2
import pymysql
import sys 

from plotly.graph_objs import *
import plotly.plotly as py 

class GenerateGraph: 
   def __init__(self, *args): 
      """
      Generate graphs based on the results in database 
      :args: 
         args  (sys.argv):list - Valules declared when calling test (shown in _help method)
      """
      if "--help" in sys.argv: 
         self._help() 
      self._get_values(sys.argv) 
      if self.psql is True:
         conn = psycopg2.connect(host=self.host, port=self.port, user=self.user, password=self.password, dbname=self.db)
         conn.autocommit = True
         self.c.cursor()
      else: 
         conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.passwd, db=self.db, autocommit=True, charset='latin1')
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
           +"\n\t--host: IP address of the PostgresSQL [--host=127.0.0.1:3306]"
           +"\n\t--user: User and password to connect to postgres [--usr=root:'passwd']"
           +"\n\t--db: Name of database being used [--db-name=test]"
           +"\n\t--psql: use PostgresSQL instead of MySQL" 
           +"\n\t--file: location where image will be stored [--file=/var/www/html]"
           +"\n\t--type: Types of graph (line, hbar, pie) [--type=line]"
           +"\n\t--title: name of the graph [--title='chart name']" 
           +"\n\t--query: SELECT statement (containing an X and Y) [--query='SELECT create_timestamp, daily_data FROM table ORDER BY create_timestamp;']"
           +"\n\t--total-only: For line graphs don't show daily results" 
           +"\n\t--daily-only: For line graphs don't show cumulative  results"  
           +"\n\tIn the case that both --total-only and --daily-only are enabled, the data generates 2 seperate graphs"
           )
      exit(1)

   def _get_values(self, values:list=[]):
      """
      Decalare values used in script
      :args: 
         self.host:str        - database IP address 
         self.port:int        - database port address 
         self.user:str        - database user 
         self.passwd:str      - database password 
         self.db:str          - database name 
         self.psql            - use PostgresSQL instead of MySQL
         self.file:str        - file in which graph will be stored 
                                Note, Plot.ly rewrites file rather than append 
         self.title:str       - Graph title
         self.type:str        - Graph type (either line or bar graph) 
         self.query:str       - Query against the original table to generate graphs 
         self.total_only:bool - generate only cumulative results 
         self.daily_only:nool - generate only non-cumulative results   
      """
      self.host = '127.0.0.1' 
      self.port = 3306 
      self.user = 'root' 
      self.passwd = 'passwd'
      self.db = 'test' 
      self.psql = False
      self.file = '/var/www/html'
      self.title = 'Graph 1' 
      self.type = 'line' 
      self.query = 'SELECT create_timestamp, daily_data FROM table ORDER BY create_timestamp;'
      self.total_only = True # if true don't generate none cumulative results 
      self.daily_only = True # if true don't generate cumulative results
      
      for value in values: 
         if value is sys.argv[0]: 
            pass 
         elif "--host" in value: 
            self.host = str(value.split("=")[-1].split(":")[0]) 
            if ":" in value:
               self.prot = str(value.split("=")[-1].split(":")[-1]) 
         elif "--user" in value: 
            self.user   = str(value.split("=")[-1].split(":")[0])
            self.passwd = str(value.split("=")[-1].split(":")[-1]) 
         elif "--db" in value: 
            self.db = str(value.split("=")[-1]) 
         elif "--psql" in value: 
            self.psql = True
         elif "--file" in value: 
            self.file = str(value.split("=")[-1]) 
         elif "--type" in value: 
            self.type = str(value.split("=")[-1])
         elif "--title" in value: 
            self.title = str(value.split("=")[-1]) 
         elif "--query" in value: 
            self.query = str(value.split("=",1)[-1])
         elif "--total-only" in value: 
            self.daily_only = False 
         elif "--daily-only" in value: 
            self.total_only = False 
         else: 
            self._help(value) 
         
   def create_temp_table(self): 
      """
      Create temporary table from which graphs will be generated 
      """
      create_table = ("CREATE TEMPORARY TABLE data(" 
                     +"\n\txaxy VARCHAR(255) DEFAULT ''," 
                     +"\n\tdaily FLOAT NOT NULL DEFAULT 0.0,"
                     +"\n\ttotal FLOAT NOT NULL DEFAULT 0.0\n);"
                     )
      self.c.execute(create_table)
   
   def insert_to_temp_table(self): 
      """
      Based on a user defined query, containing 2 rows (1 for x and another for y) generate 
      a table containing the corresponding data, and the sum of y incrementally
      """
      #self.query = "SELECT source, SUM(daily_download) FROM downloads GROUP BY source;" 
      insert = "INSERT INTO data(xaxy, daily, total) VALUES('%s', %s, %s);"
      self.c.execute(self.query) 
      results = self.c.fetchall()
      self.c.execute("SELECT COUNT(*) FROM data") 
      total = 0
      for result in results: 
         total += result[1]
         stmt = insert % (result[0], result[1], total)
         self.c.execute(stmt)

   def _retrieve_data(self, query:str='') -> dict: 
      """
      Retrieve from data to send to graph 
      :args: 
         query:str - query to be executed
      :return: 
         dict with data 
      """
      results = []
      i = 0
      self.c.execute(query) 
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
     file_name = str(datetime.datetime.now()).split(" ")[0].replace("-","_")+"_"+self.title.replace(" ", "_")+".html"
     trace_names = [] 
     if self.daily_only is True and self.total_only is False: 
        columns = self._retrieve_data("SELECT xaxy, daily FROM data ORDER BY xaxy;")
        trace_names = ['daily']
     elif self.total_only is True and self.daily_only is False: 
        columns = self._retrieve_data("SELECT xaxy, total FROM data ORDER BY xaxy;") 
        trace_names = ['total'] 
     else: 
        columns = self._retrieve_data("SELECT xaxy, daily, total FROM data ORDER BY xaxy;")
        trace_names = ['daily', 'total'] 
     # Generate trace lines
     traces = [] 
     for key in range(1, len(columns)): 
        traces.append(Scatter(x=columns[0], y=columns[key], name=trace_names[key-1])) 
     # Layout 
     layout = Layout( 
           title=self.title,
           xaxis=dict(title=xaxy), 
           yaxis=dict(title=yaxy), 
     )
     # Draw 
     data = Data(traces) 
     fig = Figure(data=data, layout=layout)
     offline.plot(fig, filename=self.file+"/"+file_name)
     f = open(self.file+"/"+file_name, 'a') 
     f.write("<body><div><center>"+self.query+"</center></div></body>")
     f.close()

   def draw_horizontal_bar_graph(self): 
     """
     Based on the results in the table, graph the output
     :args: 
        columns:dict - Dictionary of columns that are being used. 
                       Note that 0 key in columns is the X-axy, all else relate to Y-axy
        layout:Layout - Layout of graph 
        names:list - List of trace names 
     """
     yaxy = self.query.split("SELECT")[-1].split(",",1)[0].replace(" ","")
     xaxy = "count"
     columns = self._retrieve_data(self.query)
     file_name = str(datetime.datetime.now()).split(" ")[0].replace("-","_")+"_"+self.title.replace(" ", "_")+".html"
     # Generate trace lines
     traces = []
     for key in range(1, len(columns)):
        traces.append(Bar(x=columns[key], y=columns[0], orientation='h'))
     # Layout 
     layout = Layout(
           title=self.title,
           xaxis=dict(title=xaxy),
           yaxis=dict(title=yaxy),
     )

     # Draw 
     data = Data(traces)
     fig = Figure(data=data, layout=layout)
     offline.plot(fig, filename=self.file+"/"+file_name)
     f = open(self.file+"/"+file_name, 'a')
     f.write("<body><div><center>"+self.query+"</center></div></body>")
     f.close() 

   def draw_pie_graph(self): 
      """
      Based on results in the table, graph the output as pie graph
      :args: 
         data:dcit - Dictionary containing both labels and values being used 
      """
      file_name = str(datetime.datetime.now()).split(" ")[0].replace("-","_")+"_"+self.title.replace(" ", "_")+".html"
      data = self._retrieve_data(self.query)
      fig = {
         'data': [
            {
               'labels': data[0], 
               'values': data[1], 
               'type': 'pie', 
               'name': self.title, 
               'hoverinfo': 'label+percent', 
               'textinfo': 'none',
               'marker': { 
                  'colors': ['rgb(151, 154, 154)',
                             'rgb(217, 136, 128)',  
                             'rgb(230, 176, 170)', 
                             'rgb(242, 215, 213)',
                             'rgb(245, 183, 177)',
                             'rgb(249, 215, 213)',
                             'rgb(249, 235, 234)',
                             'rgb(250, 219, 216)',
                             'rgb(253, 237, 236)'
                  ]
               }
         }], 
         'layout': {
            'title': self.title,
            'showlegend': True
         }
      }
      offline.plot(fig, filename=self.file+"/"+file_name)
      f = open(self.file+"/"+file_name, 'a')
      f.write("<body><div><center>"+self.query+"</center></div></body>")
      f.close()

   def main(self):
      """
      Main to generate graphs from data
      """
      if self.type == 'hbar': 
         self.draw_horizontal_bar_graph() 
      elif self.type == 'line':
         self.create_temp_table()
         self.insert_to_temp_table()
         self.draw_line_graph() 
      elif self.type == 'pie': 
         self.create_temp_table()
         self.insert_to_temp_table()
         self.draw_pie_graph()
 
if __name__ == '__main__': 
   gg = GenerateGraph()
   gg.main()


