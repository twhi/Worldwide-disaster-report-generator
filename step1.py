# import required libraries
import requests

# start a requests session
session = requests.Session()

# request the data packet by using the URL from the developer tools
disaster_data_string = session.get('http://www.gdacs.org/xml/archive.geojson').text

# check that we've got the correct data
print(disaster_data_string)