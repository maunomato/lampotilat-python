import csv
import json
import urllib.request, json 

# https://cdn.fmi.fi/weather-observations/metadata/all-finnish-observation-stations.fi.json

url = 'https://cdn.fmi.fi/weather-observations/metadata/all-finnish-observation-stations.fi.json'

with urllib.request.urlopen(url) as json_source:
    data = json.loads(json_source.read().decode())

rows = []

for bla in data['items']:
	if bla['groups'].find('sää') != -1 and str(bla['ended']) == "None":
		#print(bla['name'] + " haz fmisid of "+str(bla['fmisid']) + str(bla['ended']))
		rows.append([bla['name'], bla['fmisid']])

with open('havaintoasemat-autom.csv', 'w', newline='') as file:
	writer = csv.writer(file, delimiter=';')
	writer.writerows(rows)