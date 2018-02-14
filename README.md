**Description**: 
The following project is intended to help users understand the location(s) from which a website was accessed, and potential visitors based on a query. 

* merge_files.py - This python file assits with merging multiple files into one. Such that when using the actual script, the program reads a single file, rather than multiple files. Thus, merge_files.py not only simplifies the process, but also enables the user to have "more"queries per Google Maps API key

* generate_ip_info.py - This is the main purpose of the code, where the program reads lines in a given access logs, and retrives the IPs and their corresponding timestamps. The code then uses Google Maps and https://freegeoip.net to find both the location, and potential companies from which the accessed IP came from. 

**Pre-Requesits**: 
* Google API Key (https://developers.google.com/maps/documentation/javascript/get-api-key) 
* Python3 (Download: https://www.python.org/)
* pygeocoder (```sudo pip3 install pygeocoder```) 
* googlemaps (```sudo pip3 install googlemaps```)
* requests (```sudo pip3 install requests```) 


**How to Use Python Script**: 

* merge_files.py 
```
# Help: 
Oris-MacBook-Pro:AccessLogs_Info_Retrieval $ python3 merge_files.py 
Error: Expect directory containing Access Logs

Oris-MacBook-Pro:AccessLogs_Info_Retrieval $ python3 merge_files.py ~/Downloads/tmp/foglamp_2018-01-26-15-26-14-EA6B7463F0FAFB30.txt 
Error: Expect directory containing Access Logs

# Notice that if everything is working properly then the system will show which file contains the merged Access Logs
Oris-MacBook-Pro:AccessLogs_Info_Retrieval $ python3 merge_files.py ~/Downloads/tmp
Merged File: /Users/ori/Downloads/tmp/merged_file_2018_02_14_10_49_28.txt
``` 

* generate_ip_info.py
```
# Help: 
Oris-MacBook-Pro:AccessLogs_Info_Retrieval $ python3 generate_ip_info.py --help
Option List: 
	--file: log file containing relevent information [--file=$HOME/tmp/site_logs.txt]
	--api-key: Google's API key to use Google Maps API [--api-key=aaaBcD123kd-d83c-C83s]
	--query: The type of location to check [--query=lunch]
	--radius: In meters how far from source to check [--radius=0]
	--timestamp:  Print a list the accessed timestamps per IP. If set to False (default), then print only the number of times that IP accessed the website

# Example with invalid option '--aaa'
Oris-MacBook-Pro:AccessLogs_Info_Retrieval $ python3 generate_ip_info.py --file=/Users/ori/Downloads/tmp/merged_file_2018_02_14_10_49_28.txt --api-key=aaaBcD123kd-d83c-C83s --query=brunch --radius=3 --timestamp --aaa 
Exception - '--aaa' is not supported

Option List: 
	--file: log file containing relevent information [--file=$HOME/tmp/site_logs.txt]
	--api-key: Google's API key to use Google Maps API [--api-key=aaaBcD123kd-d83c-C83s]
	--query: The type of location to check [--query=lunch]
	--radius: In meters how far from source to check [--radius=0]
	--timestamp:  Print a list the accessed timestamps per IP. If set to False (default), then print only the number of times that IP accessed the website
You have new mail in /var/mail/shadmonfamily

# Working example with '--timestamp'
Oris-MacBook-Pro:AccessLogs_Info_Retrieval $ python3 generate_ip_info.py --file=/Users/ori/Downloads/tmp/merged_file_2018_02_14_10_49_28.txt --api-key=aaaBcD123kd-d83c-C83s--query=brunch --radius=3 --timestamp
88.97.58.233 -
	Frequency: 4
	Timestamp: ['2018-01-26 14:58:44', '2018-01-26 14:58:26', '2018-01-26 14:58:21', '2018-01-26 14:58:32']
	Coordinates: (51.5142, -0.0931)
	Address: Queens House, London EC2V, UK
	Places: Bread Street Kitchen, Coq D'Argent, Madison, Coppa Club, Le Pain Quotidien, Bad Egg, The Folly, Temple and Sons, South Place Chop House, Carluccio's, Aubaine Broadgate Circle, London Grind, Duck & Waffle, 'Smiths' of Smithfield, Farringdon, Eastway, The Fable, The Botanist, The Modern Pantry, Searcys At The Gherkin, Chez Mal, 

# Working example without '--timestamp' 
Oris-MacBook-Pro:AccessLogs_Info_Retrieval $ python3 generate_ip_info.py --file=/Users/ori/Downloads/tmp/merged_file_2018_02_14_10_49_28.txt --api-key=aaaBcD123kd-d83c-C83s --query=brunch --radius=3 
88.97.58.233 -
	Frequency: 4
	Coordinates: (51.5142, -0.0931)
	Address: Queens House, London EC2V, UK
	Places: Bread Street Kitchen, Coq D'Argent, Madison, Millie's Lounge, Coppa Club, Bad Egg, The Folly, South Place Chop House, London Grind, Duck & Waffle, 'Smiths' of Smithfield, Farringdon, Eastway, The Fable, The Drift Bar & Restaurant, The Botanist, The Modern Pantry, New Street Grill, Foxlow Clerkenwell, Old Bengal Bar, Camino Bankside, 

```
