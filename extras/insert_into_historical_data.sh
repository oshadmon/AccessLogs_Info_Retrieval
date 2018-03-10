#!/bin/bash

# Total Number of Downloads 
grand_total=$(psql -d test -c "SELECT SUM(frequency) from ip_info;" | tail -3 | head -1) 
# Total Number of unique users 
distinct_total=$(psql -d test -c "SELECT COUNT(*) from ip_info;" | tail -3 | head -1)
# Summary of ip_history table 
json=$(psql -d test -c "SELECT ROW_TO_JSON(ip_info) FROM ip_info;" | tail -3 | head -1)
# Insert into history_data
psql -d test -c "INSERT INTO historical_data(total_access, unique_access, ip_info_table, from_where) VALUES (${grand_total}, ${distinct_total}, '${json}', 'AWS')"
