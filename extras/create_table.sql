DROP TABLE historical_data; 

-- Table containing summary of historical information
CREATE TABLE historical_data(
	   id SERIAL,
	   update_timestamp  TIMESTAMP DEFAULT now(),
	   total_access INT NOT NULL DEFAULT 0, -- Total Number of accessed  
	   unique_access INT NOT NULL DEFAULT 0, -- Total number of unique accessed 
           ip_info JSONB NOT NULL DEFAULT '{}'::jsonb, -- copy dict with information regarding everyone that accessed
	   from_where TEXT DEFAULT 'AWS', -- where is the data from (AWS/GitHub/Other)
	   PRIMARY KEY(id)
);

INSERT INTO historical_data(total_access, unique_access) VALUES (0, 0); 

