from read_file import InfoFromFile 

class TestReadFromFile: 
   def setup_class(self): 
      self.iff = InfoFromFile('/home/webinfo/AccessLogs_Info_Retrieval/source/ip_list.txt')
      self.f = open('/home/webinfo/AccessLogs_Info_Retrieval/source/ip_list.txt') 

   def teardown_class(self): 
      self.f.close() 

   def test_get_ip(self): 
      expect = ['88.97.58.233', '88.97.58.233', '88.97.58.233', '88.97.58.233', '88.97.58.233', '88.97.58.233'] 
      results = [] 
      for line in self.f.readlines(): 
         results.append(self.iff._get_ip(line))  
      assert results == expect


   def test_get_timestamp(self): 
      expect = ['2018-01-26', '2018-01-27', '2018-01-28', '2018-01-29', '2018-01-30', '2018-01-31']
      results = [] 
      for line in self.f.readlines():
         results.append(self.iff._get_timestamp(line))
      assert results == expect 
