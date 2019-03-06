# import required libraries
import requests
import json
from transform import transform_data
from output_to_csv import output_to_csv

# start a requests session
session = requests.Session()

# request the data packet by using the URL from the developer tools
disaster_data_string = session.get('http://www.gdacs.org/xml/archive.geojson').text

# convert to JSON
disaster_data = json.loads(disaster_data_string)

# transform the data
transformed_data = transform_data(disaster_data)

# output the data to CSV
output_to_csv(transformed_data)

# debug point
end = True
