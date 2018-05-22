**Description**:
The following scripts exist in order to help generate and comprehand data used by generate_info.py

**Files**:
* create_table.sql - SQL file containing the CREATE TABLE statements statements 
* retrieve_from_aws_s3.sh - The following script eases the process of retrieving data from AWS S3 bucket 
* graph.py - Based on a query related to one of the tables (in create_table.sql) generate either a bar or line graph  
* install.sh - Install script for prerequisites 

**Prerequisites**:
* [Postgres](https://www.postgresql.org/download/) or [MySQL](https://www.mysql.com/downloads/)
  * [Pgpsycopg2](https://pypi.org/project/psycopg2/)
  * [PyMySQL](https://pypi.org/project/PyMySQL/0.7.4/)
* [Python3](https://www.python.org)
   * [Plot.ly](https://plot.ly/python/) 
* [AWS Config](https://docs.aws.amazon.com/cli/latest/userguide/awscli-install-linux.html) (Optional)

**Example**: 
* graph.py Help Options
```
Option List: 
	--host: IP address of the PostgresSQL [--host=127.0.0.1:3306]
	--user: User and password to connect to postgres [--usr=root:'passwd']
	--db: Name of database being used [--db-name=test]
	--psql: use PostgresSQL instead of MySQL
	--file: location where image will be stored [--file=/var/www/html]
	--type: Types of graph (line, hbar, pie) [--type=line]
	--title: name of the graph [--title='chart name']
	--query: SELECT statement (containing an X and Y) [--query='SELECT create_timestamp, daily_data FROM table ORDER BY create_timestamp;']
	--total-only: For line graphs don't show daily results
	--daily-only: For line graphs don't show cumulative  results
	In the case that both --total-only and --daily-only are enabled, the data generates 2 seperate graphs
```
* graph.py Execute
```
~/AccessLogs_Info_Retrieval/extras$ python3 graph.py --host='127.0.0.1:3306' --user=root:passwd --db=test --query="SELECT DATE(create_timestamp), SUM(daily_download) FROM downloads GROUP BY DATE(create_timestamp) ORDER BY DATE(create_timestamp);" --type=line --title="Downloads over Time" --file=/var/www/html/
```
![downloads](https://user-images.githubusercontent.com/7193201/39894644-64559b38-545c-11e8-891b-0f94d90fc1ce.png)

* Retrival of data from AWS S3
```
~/AccessLogs_Info_Retrieval/extras$ bash retrieve_from_aws_s3.sh s3://BUCKET_NAME
download: s3://BUCKET-NAME/AccessLogs_Info_Retrieval_2018-01-26-15-26-14-EA6B7463F0FAFB30 to data/AccessLogs_Info_Retrieval_2018-01-26-15-26-14-EA6B7463F0FAFB30.txt
download: s3://BUCKET-NAME/AccessLogs_Info_Retrieval_2018-01-26-15-27-17-3F24A70952A965C6 to data/AccessLogs_Info_Retrieval_2018-01-26-15-27-17-3F24A70952A965C6.txt
download: s3://BUCKET-NAME/AccessLogs_Info_Retrieval_2018-01-26-15-27-17-DEDB702EFF21E21C to data/AccessLogs_Info_Retrieval_2018-01-26-15-27-17-DEDB702EFF21E21C.txt
download: s3://BUCKET-NAME/AccessLogs_Info_Retrieval_2018-01-26-15-27-41-299E3F3EF4DA74C9 to data/AccessLogs_Info_Retrieval_2018-01-26-15-27-41-299E3F3EF4DA74C9.txt
``` 
