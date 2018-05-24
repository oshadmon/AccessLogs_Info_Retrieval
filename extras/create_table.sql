DROP TABLE IF EXISTS raw_ip_data; 
DROP TABLE IF EXISTS ip_stats; 

CREATE TABLE raw_ip_data(
   ip VARCHAR(255) NOT NULL DEFAULT '127.0.0.1',
   source VARCHAR(255) NOT NULL DEFAULT 'AWS',
   access_timestamp TIMESTAMP DEFAULT now()
); 


