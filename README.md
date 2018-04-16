**Description**:

The following proejct is an open source tool to help people understand traction on different platform; in specific Website, GitHub, and Downloads. 

Traffic type is decided by the user, while traffic data by a user defined file. The output file should contain TIMESTAMP, and IP addresses. That way, 
it is relativly easy to calculate the frequency both by IP, and over time.  

```
# Example 1 - AWS S3 bucket file
94b0d7bdce49506054db00c7ed077b7600249ec3841c7afff89cdc3f06544e61 website [02/Feb/2018:14:56:56 +0000] 151.21.81.169 - 7BB2C5A8D6C53EAD REST.GET.OBJECT snaps/x86_64/website.info "GET /website/snaps/x86_64/website.info HTTP/1.1" 200 - 6 6 15 15 "-" "Wget/1.17.1 (linux-gnu)" -

# Example 2 - WP Engine Apache file 
180.76.15.139 - - [10/Apr/2018:00:42:52 +0000] "GET /contact-us/ HTTP/1.0" 301 - "-" "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)"t
```

Alternativly, the program can also calculate traffic for a GitHub repository. In this case, all that's required is GitHub user and password, organization name, and repository name. 
Like with a given file, the program than calculates traffic and clones; and stores them in a database. Additionally, the program also generates insight regarding where traffic is coming from under refrences. 

  
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

Files that fall under extra directory are intended to help generate data and results, but are not executed as part of the core of the project
* create_table.sql -  The following contains the create statements for the tables in which data will be stored. It is ideal to create these tables only
                      once, and then reuse them each time for better results. 
* install.sh - The following file assists with installing different components need to run code. It DOES NOT install MySQL or Postgres Database
* graph.py - Given a query generate graph with given results; based on data generated from files and/or GitHub.  
* retrieve_from_aws_s3.sh - In cases where AWS S3 is used the following helps store data into a single file 

**Prerequisites**:

* [Google API Key](https://developers.google.com/maps/documentation/javascript/get-api-key)
* [Postgres](https://www.postgresql.org/download/) or [MySQL](https://www.mysql.com/downloads/)
  * [Pgpsycopg2](https://pypi.org/project/psycopg2/) 
  * [PyMySQL](https://pypi.org/project/PyMySQL/0.7.4/) 
* [Python3](https://www.python.org)
   * [pip3](https://pip.pypa.io/en/stable/reference/pip_install/)
   * [Google Maps](https://github.com/googlemaps/google-maps-services-python)
   * [pygeocoder](https://github.com/tachang/pygeocoder)
   * [pyscopg2](https://pypi.python.org/pypi/psycopg2)
* [AWS Config](https://docs.aws.amazon.com/cli/latest/userguide/awscli-install-linux.html)

Alternatively one can run ```sudo bash $HOME/AccessLogs_Info_Retrieval/extras/install.sh```

**Example** 

* Help Options
```
Options:
	--host: database host and port           [--host=127.0.0.1:3306]
	--user: database user and password       [--user=root:passwd]
	--db:   database name                    [--db=test] 
	--source: Where the data is coming from  [--source=NewSource]
	--psql: use PostgresSQL instead of MySQL 

GitHub Requirements
	--git-auth: GitHub authentication information                                 [--git-auth='user@githbu.com':'password']
	--org: Organization that repo falls under (if none then uses GitHub username) [--org=NewOrg]
	--repo: GitHub Repository Name                                                [--repo=NewRepo]

File based insight
	--fine-name: file name and path with insight                                  [--file-name=$HOME/tmp.txt]
	--api-key: Google's API Key                                                   [--api-key=AAABBBCCC-123]
	--query: Category location falls under                                        [--query='lunch spot']
	--radius: Distance from origin                                                [--radius=0]
	--downloads: Write only to downloads table (false by default)
	--traffic: Write only to traffic table (false by default)
```

* Read from file to downloads table 
```
~/AccessLogs_Info_Retrieval$ python3 generate_info.py  --host=127.0.0.1:3306 --user=root:passwd --db=test --source=AWS --file-name=$HOME/data/output.txt --api-key=AAABBBCCC-123 --query='lunch' --radius=0  --downloads 

-- Output 
mysql> select * from downloads order by id;
+----+---------------------+--------+------+----------------+
| id | create_timestamp    | source | repo | daily_download |
+----+---------------------+--------+------+----------------+
|  1 | 2018-02-01 00:00:00 | AWS    |      |              1 |
|  2 | 2018-02-07 00:00:00 | AWS    |      |              7 |
|  3 | 2018-03-21 00:00:00 | AWS    |      |              4 |
|  4 | 2018-01-29 00:00:00 | AWS    |      |              4 |
|  5 | 2018-04-05 00:00:00 | AWS    |      |             11 |
|  6 | 2018-04-11 00:00:00 | AWS    |      |              5 |
|  7 | 2018-02-12 00:00:00 | AWS    |      |              5 |
...
```

* Read from file to traffic table 
```
~/AccessLogs_Info_Retrieval$ python3 generate_info.py --host=127.0.0.1:3306 --user=root:passwd --db=test --source=Website --file-name=/home/webinfo/website_apache_logs-2018-04-16_21-08-31.txt --api-key=AAABBBCCC-123 --query='lunch' --radius=0 --traffic

-- Output 
mysql> select * from traffic;
+----+---------------------+---------+--------------+---------------+
| id | create_timestamp    | source  | repo         | daily_traffic |
+----+---------------------+---------+--------------+---------------+
|  1 | 2018-04-09 16:29:05 | GitHub  | foglamp-pkg  |             2 |
|  2 | 2018-04-09 16:29:06 | GitHub  | foglamp-snap |             7 |
|  3 | 2018-04-09 16:29:04 | GitHub  | foglamp-gui  |            38 |
|  4 | 2018-03-26 00:00:00 | Website |              |            50 |
``` 

* Running GitHub Command - since GitHub sends data to downloads, traffic, and referrals, the example will just show referrals
```
~/AccessLogs_Info_Retrieval$ python3 generate_info.py --host=127.0.0.1:3306 --user=root:foglamp --db=test2 --source=GitHub --git-auth='user@github.com':'passwd' --org=NewOrg --repo=NewRepo

-- Output
mysql> select * from github_referral_list; 
+----+---------------------+--------------+------------------------+-----------------+
| id | create_timestamp    | repo         | referral               | daily_referrals |
+----+---------------------+--------------+------------------------+-----------------+
|  1 | 2018-04-09 16:29:03 | NewRepo      | github.com             |              20 |
|  2 | 2018-04-09 16:29:03 | NewRepo      | Google                 |              21 |
|  3 | 2018-04-09 16:29:03 | NewRepo      | Bing                   |               7 |
|  4 | 2018-04-09 16:29:03 | NewRepo      | website                |               8 |``` 
```
