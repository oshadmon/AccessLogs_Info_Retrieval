DROP TABLE IF EXISTS ip_data; 
DROP TABLE IF EXISTS github_data; 
DROP TABLE IF EXISTS github_referral_list; 
DROP TABLE IF EXISTS traffic; 
DROP TABLE IF EXISTS downloads; 

-- Table with data regarding IP address (frequency, location, potential places) 
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

-- Information regarding GitHub referrals 
CREATE TABLE github_referral_list(
   id SERIAL,
   create_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
   repo VARCHAR(255) NOT NULL DEFAULT 'NewRepo',  
   referral VARCHAR(255) NOT NULL DEFAULT '', 
   daily_referrals INT NOT NULL DEFAULT 0, 
   PRIMARY KEY(id)
); 

-- Information Downloads
CREATE TABLE downloads(
   id SERIAL,
   create_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
   source VARCHAR(255) NOT NULL DEFAULT 'GitHub', 
   repo VARCHAR(255) NOT NULL DEFAULT 'NewRepo',
   daily_download INT NOT NULL DEFAULT 0,
   PRIMARY KEY(id)
);

-- Information regarding Traffic 
CREATE TABLE traffic(
   id SERIAL,
   create_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
   source VARCHAR(255) NOT NULL DEFAULT 'GitHub',
   repo VARCHAR(255) NOT NULL DEFAULT 'NewRepo',
   daily_traffic INT NOT NULL DEFAULT 0,
   PRIMARY KEY(id)
);

