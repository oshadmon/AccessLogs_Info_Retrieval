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
      if "--help" in sys.argv:
         self._help()
      self._declare_values(values=sys.argv)

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
      self.query = "SELECT * FROM table;"
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
            self.query = str(value.split("=")[-1]) 
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

   def retrieve_data(self) -> dict: 
      """
      Retrieve data from database based on a given query 
      :return: 
         Result of the query in a dictionary. Poisition 0 of the dictionary correlates to X, and all consequent rows correlate to Y
      """ 
      results = []
      # DB interaction
      conn = pymysql.connect(host=self.host, user=self.usr, password=self.passwd, db=self.dbname, autocommit=True, charset='latin1')
      c = conn.cursor() 
      c.execute(self.query) 
      for result in c.fetchall(): 
         results.append(result)
      c.close() 

      # Store results from database in dict (0 by default is X, and any consecutive number is the "Y" for that givne X
      column={}
      for v in range(len(results[0])):
        column[v]=[]
      for result in results: 
         for key in column.keys(): 
            column[key].append(result[key])
      return column

   def trace_names(self) -> list: 
      """
      Based on the query generate values generate names of traces, and x-axy 

      Example: SELECT column0, column1, column2 FROM table
         - column0 correlates to X-axy name 
         - column1 and column2 correlate to line names
      :return:
         Return the name of the x-axy and traces 
      """  
      traces=[]
      xname=''
      layout = None
      # Generate names 
      for column in self.query.lower().split("select")[-1].split("from")[0].split(","):
         if xname is '': 
            xname = column.split("(")[-1].split(")")[0].replace("`","")
         else: 
            traces.append(column.split("(")[-1].split(")")[0].replace("`",""))

      return xname, traces
                     
   def _output_file(self): 
      file_name=str(datetime.datetime.now().date()).replace("-","_")+"_"+self.title.replace(" ","_")+".html"
      if "/" is self.file[-1]: 
         self.file += file_name
      else: 
         self.file += "/"+file_name

   def draw_line_graph(self, columns:dict={}, xname='', trace_names=[]): 
     """
     Based on the results in the table, graph the output
     :args: 
        columns:dict - Dictionary of columns that are being used. 
                       Note that 0 key in columns is the X-axy, all else relate to Y-axy
        layout:Layout - Layout of graph 
        names:list - List of trace names 
     """ 
     # Generate trace lines
     traces = [] 
     for key in range(1, len(columns)): 
        traces.append(Scatter(x=columns[0], y=columns[key], name=trace_names[key-1])) 
     # Layout 
     layout = Layout(
                    title = self.title,
                    xaxis = dict(title=xname)
              )

     # Draw 
     data = Data(traces) 
     fig = Figure(data=data, layout=layout)
     offline.plot(fig, filename=self.file)

   def draw_hbar_graph(self, columns:dict={}, xname='', trace_names=[]):
     """
     Based on the results in the table, graph the output
     :args: 
        columns:dict - Dictionary of columns that are being used. 
                       Note that 0 key in columns is the X-axy, all else relate to Y-axy
        layout:Layout - Layout of graph 
        names:list - List of trace names 
     """
     # Generate trace lines
     traces = []
     for key in range(1, len(columns)):
        traces.append(Bar(x=columns[key], y=columns[0], name=trace_names[key-1], orientation='h'))
     # Layout 
     layout = Layout(
                    title = self.title,
                    yaxis = dict(title=xname)
              )

     # Draw 
     data = Data(traces)
     fig = Figure(data=data, layout=layout)
     offline.plot(fig, filename=self.file)


   def main(self):
      """
      Main to generate graphs from data
      """
      # Get data 
      columns = self.retrieve_data()
      # Get graph info 
      xname, traces = self.trace_names() 
      self._output_file() 
      # draw graph  
      if self.type == "line":
         self.draw_line_graph(columns, xname, traces)  
      elif self.type == "hbar": 
         self.draw_hbar_graph(columns, xname, traces) 
      
 
if __name__ == '__main__': 
   gg = GenerateGraph()
   gg.main()
