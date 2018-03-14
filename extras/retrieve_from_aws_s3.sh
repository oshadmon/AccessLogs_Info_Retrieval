#!/bin/bash

# The following iterates through S3 bucket and retrieves information from it. All the information in a given bucket is then stored into a single file 

if [ -z "${1}" ]
then 
   echo "Missing S3 Bucket URL [ex. bash extras/retrieve_from_aws_s3.sh s3://website-analytics]" 
   exit 1 
fi 
 
url=$1

rm -rf  /home/webinfo/data 
mkdir /home/webinfo/data 

touch /home/webinfo/data/file_names.txt 

aws s3 ls ${url} | awk -F " " '{print $4}' | sort -u > /home/webinfo/data/file_names.txt 
for f in $( cat /home/webinfo/data/file_names.txt )
do 
#   echo $f 
   aws s3 cp s3://dianomic-analytics/${f} /home/webinfo/data/${f}.txt
   cat /home/webinfo/data/${f}.txt >> /home/webinfo/data/output.txt
   rm -rf /home/webinfo/data/${f}.txt 
done 
