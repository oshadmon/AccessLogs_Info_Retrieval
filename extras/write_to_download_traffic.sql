/*
Insert into traffic and download tables in order to generate graphs 
*/

-- Insert GitHub Data into downloads and traffic
INSERT INTO downloads(source, create_timestamp, total_download, unique_download) SELECT 'GitHub',  DATE(create_timestamp), SUM(total), SUM(uniques) FROM github_data WHERE DATE(create_timestamp)=DATE(now()) AND info='clones' GROUP BY date(create_timestamp) ;

INSERT INTO traffic(source, create_timestamp, total_traffic, unique_traffic) SELECT 'GitHub',  date(create_timestamp), SUM(total), SUM(uniques) FROM github_data WHERE DATE(create_timestamp)=DATE(now()) AND info='traffic' GROUP BY date(create_timestamp) ;

-- Insert into Downloads (AWS) 
INSERT INTO downloads(source, create_timestamp, unique_download) SELECT 'AWS', DATE(update_timestamp), COUNT(*) FROM ip_data WHERE DATE(update_timestamp)=DATE(NOW()) AND source='AWS' GROUP BY DATE(update_timestamp);

UPDATE downloads set total_download=(SELECT COUNT(*) FROM ip_data WHERE source='AWS') WHERE create_timestamp=DATE(NOW()) AND source='AWS';   

-- Insert into traffic (Website) 
INSERT INTO traffic(source, create_timestamp, unique_traffic) SELECT 'website', DATE(update_timestamp), COUNT(*) FROM ip_data WHERE DATE(update_timestamp)=DATE(NOW()) AND source='website' GROUP BY DATE(update_timestamp); 

UPDATE traffic SET total_traffic=(SELECT COUNT(*) FROM ip_data WHERE source='website') WHERE create_timestamp=DATE(NOW()) AND source='website';

