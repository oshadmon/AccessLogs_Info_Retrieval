#!/bin/bash
# Installation requirements code 
apt-get install update
# Postgres
apt-get install postgresql
# Python3 
apt-get install python3
# Pip3
apt-get install python3-pip
# Non-standard Python3 packages  
pip3 install pygeocoder
pip3 install googlemaps3
pip3 install requests
pip3 install psycopg2-binary
# AWS
pip3 install --upgrade awscli



