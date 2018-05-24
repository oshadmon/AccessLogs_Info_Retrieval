**Description**:
The following script helps take download and traffic information, either from GitHub or text file, and send it into a local database for ease of analysis. 

This version of the code just does IP counting

**Files**:
* generate_info.py - The following piece of code is the "main' of the entire project. Through here a user can what they want to run. 
* generate_ip_info.py - This piece of code focuses entirly on generating information from a given file. It is broken down into 3 componente: 
   - GenerateIPBasedInfo: The main of the three parts, where the file runs through it's course, and combines information in order to generate the final result. 
                          It is also here where data is sent ot the database as either traffic, downloads, and/or ip insight. In the case of ip insight, the information
                          that was originally stored as a dictionary is sent to MySQL table named "ip_data".                    
   - InfoFromFile: The following reads through the file, and retrieves the IP and TIMESTAMPS. It is important to note that each IP may have one timestamp per day; 
                   meaning that if an IP accessed a site multiple times during a given day it is only counted once.  

   - LocationInfo: Given an IP address, generate location and potential visitors (by query)
* generate_github_info.py - In this case, the code generates information regarding a GitHub repository 
   - GenerateGitHubInfo: The following is the main of two parts. In this case, the code sends generated data into an appropriate table. 
   - GitHub: Given authentication, organizition, and repostiory name the following generates traffic, clones, and referrals from GitHub insight.    

**Prerequisites**:
* [Postgres](https://www.postgresql.org/download/) or [MySQL](https://www.mysql.com/downloads/)
  * [Pgpsycopg2](https://pypi.org/project/psycopg2/) 
  * [PyMySQL](https://pypi.org/project/PyMySQL/0.7.4/) 
* [Python3](https://www.python.org)
   * [pip3](https://pip.pypa.io/en/stable/reference/pip_install/)
   * [pygeocoder](https://github.com/tachang/pygeocoder)
   * [pyscopg2](https://pypi.python.org/pypi/psycopg2)
* [AWS Config](https://docs.aws.amazon.com/cli/latest/userguide/awscli-install-linux.html) (Optional)

Alternatively one can run ```sudo bash $HOME/AccessLogs_Info_Retrieval/extras/install.sh```

**Example** 

* Help Options
```
~/AccessLogs_Info_Retrieval$ python3 generate_info.py --help 
usage: generate_info.py [-h] [-query QUERY] [-radius RADIUS]
                        [--no-download NO_DOWNLOAD] [--no-traffic NO_TRAFFIC]
                        host user dbname source data_file api_key

positional arguments:
  host                  host/port connection to database [127.0.0.1:5432]
  user                  user/password to database [root:passwd]
  dbname                database name [test]
  source                Where data is coming from [AWS or Website]
  data_file             File containing data to be sent to database
  api_key               Google Maps API Key

optional arguments:
  -h, --help            show this help message and exit
  -query QUERY          Search query
  -radius RADIUS        Search radius
  --no-download NO_DOWNLOAD
                        Write only to traffic table
  --no-traffic NO_TRAFFIC
                        Write only to downloads table
```
