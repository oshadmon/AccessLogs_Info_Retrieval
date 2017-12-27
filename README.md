**Description**: 

Given a generic Wordpress Engine Log file, the following script, format's the file to human readable. When done the user will know: 
1) DNS IP address 
2) How many times the address accessed the site 
3) Coordinates / Address of DNS IP 
4) Potential near by places based on query (ideal for B2B comapnies wanting to find potential clients) 

**Pre-Requesits**: 
* Google API Key (https://developers.google.com/maps/documentation/javascript/get-api-key) 
* Python3 (Download: https://www.python.org/)
* pygeocoder (```sudo pip3 install pygeocoder```) 
* googlemaps (```sudo pip3 install googlemaps```)
* requests (```sudo pip3 install requests```) 

**How to get Access Logs**: 
1. Go to WPEngine & Login (https://my.wpengine.com/) 
2. On the righthand toolbar you'll see "Access Logs" (press that) 
3. You can then download your logfiles 

**How to Use Python Script**: 

_Get Help_:
```
MacBook-Pro:CleanWordPressEngineAccessLog $ python3 locaton_genorator_main.py --help 
The following assits with generating info regarding
	--file: WordPress Access Log file            [--file=$HOME/tmp/nginx_logs.txt]
	--api-key: The Google API Key                [--api-key=aaaBcD123kd-d83c-C83s]
	--query: what you are looking for            [--query='lunch']
	--radius: distance (in meters) from location [--radius=0]
	--disable-timestamp: remove list of access timestamp from output
	--disable-coordinates: remove coordinates from output
	--disable-address: remove address from output
	--disable-query: remove info relating to near by places from output
	--help: provides info on how to use script
```

_Example_: 

The following example takes a file (called sample.txt), which has Access Log information and converts it to human readable  

Sample Raw File File: 
```
MacBook-Pro:CleanWordPressEngineAccessLog $ cat sample.txt 
66.249.79.52 google.com - [20/Dec/2017:00:21:42 +0000] "GET /robots.txt HTTP/1.1" 200 67 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
66.249.79.58 google.com - [20/Dec/2017:00:21:43 +0000] "GET /blog/why-is-fog-computing-good-for-mysql/ HTTP/1.1" 200 10387 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
173.13.145.225 google.com - [20/Dec/2017:00:24:12 +0000] "GET / HTTP/1.1" 200 5141 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"
173.13.145.225 google.com - [20/Dec/2017:00:24:12 +0000] "GET /wp-content/plugins/ultimate-author-box-lite/css/frontend.css?ver=1.0.3 HTTP/1.1" 200 34290 "http://google.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"
```

Run Query: 
```
MacBook-Pro:CleanWordPressEngineAccessLog $ python3 locaton_genorator_main.py  --file=$HOME/CleanWordPressEngineAccessLog/sample.txt --api-key=AIzaSyBkVEF5smFYx9fGp-WuxrxpDQXeLrVt-PA --query='Brunch' --radius=5
```

Output: 
```
MacBook-Pro:CleanWordPressEngineAccessLog $ cat sample.txt 
173.13.145.225 -
	Frequency: 2
	Timestamps: 
		['2017-12-20 00:24:12', '2017-12-20 00:24:12']
	Coordinates: (37.751, -97.822)
	Address: Unnamed Road, Mt Hope, KS 67108, USA
	Potential Query Results: 
		['Creations Restaurant', 'Pizza Hut', "Scooter's Coffee", 'TWELVE Restaurant & Bar', "Applebee's Neighborhood Grill & Bar", 'SUBWAY®Restaurants', 'Sonic Drive-In', 'Taco Bell', 'Sonic Drive-In', 'SUBWAY®Restaurants', 'HomeGrown Wichita', 'IHOP', "Arby's", 'LongHorn Steakhouse', 'Five Guys', 'Spangles', "Jose Pepper's Mexican Restaurant", "Jimmie's Diner", 'Old Chicago Pizza and Taproom', "Arby's"]
66.249.79.58 -
	Frequency: 1
	Timestamps: 
		['2017-12-20 00:21:43']
	Coordinates: (37.4192, -122.0574)
	Address: H Ln, Mountain View, CA 94043, USA
	Potential Query Results: 
		['The Voya Restaurant', "Roger's Deli & Donuts", 'Michaels At Shoreline', 'Olympus Caffe & Bakery', 'Faz', 'Eureka!', 'Steins', 'KopëPot', 'Crepevine', 'Jack in the Box', 'Bajis Cafe', "Omelette House @ Ava's", 'Sushi Tomi', "Hobee's Restaurant", 'Scratch', 'Bierhaus', "Denny's", 'iBagel Bakery & Cafe', 'Hobee’s Restaurant', 'Yami Grill']
66.249.79.52 -
	Frequency: 1
	Timestamps: 
		['2017-12-20 00:21:42']
	Coordinates: (37.4192, -122.0574)
	Address: H Ln, Mountain View, CA 94043, USA
	Potential Query Results: 
		['The Voya Restaurant', "Roger's Deli & Donuts", 'Michaels At Shoreline', 'Olympus Caffe & Bakery', 'Faz', 'Eureka!', 'Steins', 'KopëPot', 'Crepevine', 'Jack in the Box', 'Bajis Cafe', "Omelette House @ Ava's", 'Sushi Tomi', "Hobee's Restaurant", 'Scratch', 'Bierhaus', "Denny's", 'iBagel Bakery & Cafe', 'Hobee’s Restaurant', 'Yami Grill']
```

