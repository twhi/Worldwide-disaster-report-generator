# import required libraries
import requests
import json
from transform import transform_data

# start a requests session
session = requests.Session()

# request the data packet by using the URL from the developer tools
disaster_data_string = session.get('http://www.gdacs.org/xml/archive.geojson').text

# convert to JSON
disaster_data = json.loads(disaster_data_string)

# transform the data
output = transform_data(disaster_data)

# debug point
end = True
