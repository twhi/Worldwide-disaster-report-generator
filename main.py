# import required libraries
import requests
import json
from datetime import datetime
import urllib.parse as urlparse
from bs4 import BeautifulSoup
import re
import csv


def construct_geojson_url(d):
    link = d['properties']['link']
    parsed_url = urlparse.urlparse(link)
    eventtype = urlparse.parse_qs(parsed_url.query)['eventtype']
    eventid = urlparse.parse_qs(parsed_url.query)['eventid']
    episodeid = urlparse.parse_qs(parsed_url.query)['episodeid']
    return "http://www.gdacs.org//datareport/resources/{0}/{1}/geojson_{1}_{2}.geojson".format(eventtype[0], eventid[0],
                                                                                               episodeid[0])


def get_extra_info(table):
    tds = [row.findAll('td') for row in table.findAll('tr')]
    return {re.sub(r'\W+', '', td[0].string).lower(): td[1].text for td in tds}


def parse_extra_info(i, type):
    if type == "Drought":
        return {
            'impact': i['impact']
        }
    elif type == "Earthquake":
        return {
            'depth': i['depth'],
            'exposed_population': i['exposedpopulation']
        }
    elif type == "Tropical Cyclone":
        return {'name': i['name'],
                'max_wind_speed': i['maximumwindspeed'],
                'max_storm_surge': i['maximumstormsurge'],
                'exposed_population': i['exposedpopulation'],
                'vulnerability': i['vulnerability']
                }
    elif type == "Flood":
        return {
            'death_toll': i['peoplekilled'],
            'people_displaced': i['peopledisplaced']
        }
    elif type == "Volcano":
        return {
            'name': i['volcanoeruption'],
            'exposed_population': i['exposedpopulation']
        }


d_key = {
    'DR': 'Drought',
    'TC': 'Tropical Cyclone',
    'FL': 'Flood',
    'EQ': 'Earthquake',
    'VO': 'Volcano'
}

session = requests.Session()
disaster_data_string = session.get('http://www.gdacs.org/xml/archive.geojson').text
disaster_data = json.loads(disaster_data_string)
disasters = disaster_data['features']

output = {}
for disaster in disasters:
    # get disaster type
    type_id = disaster['id'][:2]
    d_type = d_key[type_id]

    # if key isn't already in the output variable then add it
    if d_type not in output:
        output[d_type] = []

    # extra info
    summary = session.get(disaster['properties']['link']).text
    soup = BeautifulSoup(summary, features='html.parser')
    tab = soup.find("table", {"class": "summary"})
    extra_info = get_extra_info(tab)
    parsed_extra_info = parse_extra_info(extra_info, d_type)

    # further disaster specific data
    geojson_url = construct_geojson_url(disaster)
    try:
        disaster_geo = json.loads(session.get(geojson_url).text)
        alert_score = disaster_geo['features'][0]['properties']['alertscore']
    except:
        alert_score = 0

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

    # get more params
    alert_level = disaster['properties']['alertlevel']
    severity_index = disaster['properties']['severity']
    country_list = disaster['properties']['countrylist']
    coordinates = {'x': disaster['geometry']['coordinates'][1], 'y': disaster['geometry']['coordinates'][0]}

    # add data to output variable
    disaster_data = {
        'further_info': disaster['properties']['link'],
        'alert_level': alert_level,
        'alert_score': alert_score,
        'severity': severity_index,
        'location': country_list,
        'start_date': start_date,
        'end_date': end_date,
        'duration': duration,
        'ongoing': ongoing,
        'coordinates': coordinates,
    }
    disaster_data.update(parsed_extra_info)
    output[d_type].append(disaster_data)

    print('#####################')
    print(d_type, 'in', country_list)
    print('Disaster started on', start_date)
    if ongoing:
        print('Disaster is ongoing')
    else:
        print('Disaster ended on', end_date)
    print('Severity index -', severity_index)


for d in output:
    keys = output[d][0].keys()
    with open(d+'.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(output[d])

# debug point
ender = True
