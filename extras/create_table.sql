DROP TABLE IF EXISTS historical_data; 
DROP TABLE IF EXISTS ip_data; 
DROP TABLE IF EXISTS github_data; 
DROP TABLE IF EXISTS github_referral_list; 

-- Table containing summary of historical information
CREATE TABLE historical_data(
   id SERIAL,
   create_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
   total_access INT NOT NULL DEFAULT 0, -- Total Number of accessed  
   unique_access INT NOT NULL DEFAULT 0, -- Total number of unique accessed 
   ip_data JSON NOT NULL, -- copy dict with information regarding everyone that accessed
   source VARCHAR(255) DEFAULT 'AWS', -- where is the data from (AWS/GitHub/Other)
   PRIMARY KEY(id)
);
CREATE INDEX source_index ON historical_data(source); 
 
-- Table with BLOB information regarding AWS broken down 
-- If ip exists in table then only `total_access` and `frequency` get updated, otherwise keep new row is added  
CREATE TABLE ip_data(
   id SERIAL, 
   create_timestamp TIMESTAMP DEFAULT now(), 
   update_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
   ip VARCHAR(255) NOT NULL DEFAULT '127.0.0.1', 
   source VARCHAR(255) NOT NULL DEFAULT 'AWS', 
   total_access INT NOT NULL DEFAULT 0, -- Total Number of accessed  
   access_times TEXT, -- AWS Accessed Timestamps 
   coordiantes VARCHAR(255), -- Coordinates 
   address VARCHAR(255) NOT NULL DEFAULT '', -- Address
   places TEXT, -- Places
   PRIMARY KEY (id)
); 
CREATE INDEX source ON ip_data(source, ip); 

-- Table with information regarding GitHub Repositories 
CREATE TABLE github_data(
   id SERIAL, 
   create_timestamp TIMESTAMP NOT NULL DEFAULT NOW(), 
   update_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   repo VARCHAR(255) NOT NULL DEFAULT 'NewRepo', -- Repository data is coming from 
   info VARCHAR(255) NOT NULL DEFAULT 'clone', -- Type of data (traffic / clone / reference)
   total INT NOT NULL DEFAULT 0, 
   uniques INT NOT NULL DEFAULT 0, 
   PRIMARY KEY(id) 
); 
CREATE UNIQUE INDEX repo_info_index ON github_data(repo, info); 

-- Information regarding referrals 
CREATE TABLE github_referral_list(
   id SERIAL,
   create_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
   update_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   referral VARCHAR(255) NOT NULL DEFAULT '', 
   unique_referrals INT NOT NULL DEFAULT 0, 
   count_referrals INT NOT NULL DEFAULT 0,
   PRIMARY KEY(id)
); 
CREATE UNIQUE INDEX referral_index ON github_referral_list(referral); 
