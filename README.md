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

[Test Samples](#Examples)
  
**Files**:


**Prerequisites**:

* [Google API Key](https://developers.google.com/maps/documentation/javascript/get-api-key)
* [Postgres](https://www.postgresql.org/download/)
* [Python3](https://www.python.org)
   * [pip3](https://pip.pypa.io/en/stable/reference/pip_install/)
   * [Google Maps](https://github.com/googlemaps/google-maps-services-python)
   * [pygeocoder](https://github.com/tachang/pygeocoder)
   * [pyscopg2](https://pypi.python.org/pypi/psycopg2)
* [AWS Config](https://docs.aws.amazon.com/cli/latest/userguide/awscli-install-linux.html)

Alternatively one can run ```sudo bash $HOME/AccessLogs_Info_Retrieval/extras/install.sh```

**Example** 

In order for repository to work the user must execute the following  
Install prerequisites & Configure AWS
Create database table 
Execute extras/retrive_from_aws_s3.sh which gets information from S3
Execute ```generate_ip_info.py``` - this will also execute ``retrieve_from_github.py```

```
# Help
ubuntu:~/AccessLogs_Info_Retrieval$ bash extras/retrieve_from_aws_s3.sh 
Missing S3 Bucket URL [ex. bash extras/retrieve_from_aws_s3.sh s3://website-analytics]

ubuntu:~/AccessLogs_Info_Retrieval$ python3 generate_ip_info.py  --help
Option List: 
	--file: log file containing relevent information [--file=$HOME/tmp/site_logs.txt]
	--api-key: Google's API key to use Google Maps API [--api-key=aaaBcD123kd-d83c-C83s]
	--query: The type of location to check [--query=lunch]
	--radius: In meters how far from source to check [--radius=0]
	--timestamp:  Print a list the accessed timestamps per IP. If set to False (default), then print only the number of times that IP accessed the website
	--stdout: print to screen otherwise will just store to database (default false)
	--host: IP address of the PostgresSQL [--host=127.0.0.1]
	--usr: User and password to connect to postgres [--usr=root:'']
	--db-name: Name of database being used [--db-name=test]

ubuntu:~/AccessLogs_Info_Retrieval$ python3 generate_ip_info_github.py  --help
Option List: 
	--host: IP address of the PostgresSQL [--host=127.0.0.1]
	--usr: User and password to connect to postgres [--usr=root:'']
	--db-name: Name of database being used [--db-name=test]
	--git-usr: Usernamne and password to access git [--git-usr='user@github.com':'password']
	--git-org: Organization under which repository exists [--git-org='user']
	--git-repo: Repository name [--git-repo=NewRepo,NewRepo2]
	--stdout: print to screen otherwise will just store to database (default false)

# Execute 
ubuntu:~/AccessLogs_Info_Retrieval$ bash extras/retrieve_from_aws_s3.sh s3://bucket-name 
download: s3://bucket-name/test_2018-01-26-15-26-14-EA6B7463F0FAFB30 to ../data/foglamp_2018-01-26-15-26-14-EA6B7463F0FAFB30.txt

ubuntu:~/AccessLogs_Info_Retrieval$ cat ~/data/output.txt 
94b0d7bdce49506054db00c7ed077b7600249ec3841c7afff89cdc3f06544e61 test [26/Jan/2018:14:58:44 +0000] 88.97.58.233 

ubuntu:~/AccessLogs_Info_Retrieval$ time python3 generate_ip_info.py --file=/home/usr/data/output.txt --api-key=aaaBcD123kd-d83c-C83sI --usr=usr:passwd --git-repo=AccessLogs_Info_Retrieval --git-usr=usr@github.com:passwd --stdout 
88.97.58.233 -
	Frequency: 12
	Coordinates: (51.5142, -0.0931)
	Address: Queens House, London EC2V, UK
	Places: Failed to get potential lunch places due to API Key limit. For more info: https://developers.google.com/maps/documentation/javascript/get-api-key

ubuntu:~/AccessLogs_Info_Retrieval$ time python3 generate_ip_info.py --usr=usr:passwd --git-repo=AccessLogs_Info_Retrieval --git-usr=usr@github.com:passwd --stdout
Clones - 
	Total: 2 | Unique: 2
Traffic -
	Total: 142 | Unique: 2
Referreral - 
	Total: 22 | Unique: 1 | Origin: github.com

```



