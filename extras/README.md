**Description**:
The following scripts exist in order to help generate and comprehand data used by generate_info.py

**Files**:
* create_table.sql - SQL file containing the CREATE TABLE statements statements 
* retrieve_from_aws_s3.sh - The following script eases the process of retrieving data from AWS S3 bucket 
* install.sh - Install script for prerequisites 

**Prerequisites**:
* [AWS Config](https://docs.aws.amazon.com/cli/latest/userguide/awscli-install-linux.html) (Optional)


* Retrival of data from AWS S3
```
~/AccessLogs_Info_Retrieval/extras$ bash retrieve_from_aws_s3.sh s3://BUCKET_NAME
download: s3://BUCKET-NAME/AccessLogs_Info_Retrieval_2018-01-26-15-26-14-EA6B7463F0FAFB30 to data/AccessLogs_Info_Retrieval_2018-01-26-15-26-14-EA6B7463F0FAFB30.txt
download: s3://BUCKET-NAME/AccessLogs_Info_Retrieval_2018-01-26-15-27-17-3F24A70952A965C6 to data/AccessLogs_Info_Retrieval_2018-01-26-15-27-17-3F24A70952A965C6.txt
download: s3://BUCKET-NAME/AccessLogs_Info_Retrieval_2018-01-26-15-27-17-DEDB702EFF21E21C to data/AccessLogs_Info_Retrieval_2018-01-26-15-27-17-DEDB702EFF21E21C.txt
download: s3://BUCKET-NAME/AccessLogs_Info_Retrieval_2018-01-26-15-27-41-299E3F3EF4DA74C9 to data/AccessLogs_Info_Retrieval_2018-01-26-15-27-41-299E3F3EF4DA74C9.txt
``` 
