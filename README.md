**Description**: 
The following project is intended to help with understanding web traffic. 
In this instance the script takes IP address and timestamps, and then returns geolocation, and potential places based on user defined queries. 
This tool is intended to assist understanding of who accessed a given site. 

Files 
* generate_ip_info.py - The generate_ip_info script takes a file containing IP and timestamps, and iterates through them to find geolocation, and potential near by places (defined by query). It then takes the relevent information, and sends it into a database table such that it is easily retrived, and accessible. 
* extras/retrive_from_aws_s3.sh - Using AWS bucket URL retrive all information from bucket (files). The files are merged into one (1) file to be used by generate_ip_info.py. 
* extras/create_table.sql - SQL table and initial line required for generate_ip_info.py   


**Pre-Requesits**: 
* [Google API Key](https://developers.google.com/maps/documentation/javascript/get-api-key) 
* [Postgres](https://www.postgresql.org/download/) 
* [Python3](https://www.python.org)
   * [pip3](https://pip.pypa.io/en/stable/reference/pip_install/) 
   * [Google Maps](https://github.com/googlemaps/google-maps-services-python) 
   * [pygeocoder](https://github.com/tachang/pygeocoder) 
   * [pyscopg2](https://pypi.python.org/pypi/psycopg2) 
* [AWS Config](https://docs.aws.amazon.com/cli/latest/userguide/awscli-install-linux.html) 

Alternativly one can run ```sudo bash $HOME/AccessLogs_Info_Retrieval/extras/install.sh``` 

**How to Use Python Script**: 

```
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
```
