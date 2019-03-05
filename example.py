# import required libraries
import requests
import json
from datetime import datetime
import urllib.parse as urlparse
from bs4 import BeautifulSoup


def construct_geojson_url(d):
    link = d['properties']['link']
    parsed_url = urlparse.urlparse(link)
    eventtype = urlparse.parse_qs(parsed_url.query)['eventtype']
    eventid = urlparse.parse_qs(parsed_url.query)['eventid']
    episodeid = urlparse.parse_qs(parsed_url.query)['episodeid']
    return "http://www.gdacs.org//datareport/resources/{0}/{1}/geojson_{1}_{2}.geojson".format(eventtype[0], eventid[0],
                                                                                               episodeid[0])


# create requests session
session = requests.Session()

# use the requests session to get the json packet
disaster_data_string = session.get('http://www.gdacs.org/xml/archive.geojson').text

# use json.loads to create a json (or dictionary in Python speak) object from a string
disaster_data = json.loads(disaster_data_string)

# get all of the disaster data in the 'features' slot
disasters = disaster_data['features']

# disaster type key
d_key = {
    'DR': 'Drought',
    'TC': 'Tropical Cyclone',
    'FL': 'Flood',
    'EQ': 'Earthquake',
    'VO': 'Volcano'
}

output = {}
for disaster in disasters:

    # event summary
    summary = session.get(disaster['properties']['link']).text
    soup = BeautifulSoup(summary, features='html.parser')
    tab = soup.find("table", {"class": "summary"})
    cells = tab.findAll("td")

    switch = 0
    outlist = []
    for values in cells:
        if switch == 0:
            text = values.text
            switch += 1
        else:
            text += "; " + values.text
            switch = 0
            outlist.append(text.lower())
    print(outlist)

    # further disaster specific data
    geojson_url = construct_geojson_url(disaster)
    try:
        disaster_geo = json.loads(session.get(geojson_url).text)
        alert_score = disaster_geo['features'][0]['properties']['alertscore']
    except:
        alert_score = 0

    # get disaster type
    type_id = disaster['id'][:2]
    d_type = d_key[type_id]

    # if key isn't already in the output variable then add it
    if d_type not in output:
        output[d_type] = []

    # get start and end dates and calculate duration of disaster
    start_date_h = datetime.strptime(disaster['properties']['fromdate'], '%d/%b/%Y %H:%M:%S')
    start_date = datetime(start_date_h.year, start_date_h.month, start_date_h.day)
    end_date_h = datetime.strptime(disaster['properties']['todate'], '%d/%b/%Y %H:%M:%S')
    end_date = datetime(end_date_h.year, end_date_h.month, end_date_h.day)
    duration = end_date - start_date

    # calculate if the disaster is ongoing
    ongoing = False
    if end_date.date() == datetime.today().date():
        ongoing = True

    # get alert level
    alert_level = disaster['properties']['alertlevel']

    # severity index
    severity_index = disaster['properties']['severity']

    # country list
    country_list = disaster['properties']['countrylist']

    # coordinates
    coordinates = {'x': disaster['geometry']['coordinates'][1], 'y': disaster['geometry']['coordinates'][0]}

    # add data to output variable
    output[d_type].append({
        'alert_level': alert_level,
        'alert_score': alert_score,
        'severity': severity_index,
        'location': country_list,
        'start_date': start_date,
        'end_date': end_date,
        'duration': duration,
        'ongoing': ongoing,
        'coordinates': coordinates
    })

    print('Disaster type:', d_type)
    print('Severity Index:', severity_index)
    print('Alert score:', alert_score)
    print(disaster['properties']['link'])
    print('#####################')

json_output = json.dumps(output, default=str)
f = open('output.txt', 'w')
f.write(json_output)
f.close()

# debug point
ender = True
