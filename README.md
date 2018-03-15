**Description**:

The following project is intended to help with understanding web traffic. In this instance the script takes IP address and timestamps, and then returns geolocation, and potential places based on user defined queries. This tool is intended to assist understanding of who accessed a given site.


**Files**:

* generate_ip_info.py - The generate_ip_info script takes a file containing IP and timestamps, and iterates through them to find geolocation, and potential near by places (defined by query). It then takes the relevant information, and sends it into a database table such that it is easily retrieved, and accessible.
* install.sh - installation script for all prerequisites. The script doesn't not configure AWS 
* extras/create_table.sql - SQL table and initial line required for generate_ip_info.py
* extras/retrive_from_aws_s3.sh - Using AWS bucket URL retrieve all information from bucket (files). The files are merged into one (1) file to be used by generate_ip_info.py.
* extras/retrieve_from_github.py - Using GitHub insight retrieve clone and traffic information regarding a repository. 

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

**Process & Example** 

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
        --file: log file containing relevant information [--file=$HOME/tmp/site_logs.txt]
        --api-key: Google's API key to use Google Maps API [--api-key=aaaBcD123kd-d83c-C83s]
        --query: The type of location to check [--query=lunch]
        --radius: In meters how far from source to check [--radius=0]
        --timestamp:  Print a list the accessed timestamps per IP. If set to False (default), then print only the number of times that IP accessed the website
        --stdout: print to screen otherwise will just store to database (default false)
        --host: IP address of the PostgresQL [--host=127.0.0.1]
        --usr: User and password to connect to postgres [--usr=root:'']
        --db-name: Name of database being used [--db-name=test]
        --git-usr: Username and password to access git [--git-usr='user@github.com':'password']
        --git-org: Organization under which repository exists [--git-org='user']
        --git-repo: Repository name [--git-repo=NewRepo]

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
{'clones': [{'timestamp': '2018-03-02T00:00:00Z', 'uniques': 1, 'count': 1}, {'timestamp': '2018-03-08T00:00:00Z', 'uniques': 1, 'count': 1}], 'uniques': 2, 'count': 2}

Clones - 
	Total: 2 | Unique: 2
Traffic -
	Total: 142 | Unique: 2
Referreral - 
	Total: 22 | Unique: 1 | Origin: github.com

```



