import pygeocoder as geo
from wxtalk import helper
import csv
import time
import requests
#Just some scrap code to update my master station list with city names, states and timezones
#Steve Zimmerman, 25JUN2015


string = "col0,col1,WV PETERSBURG,col3,KW99,39.0,-79.15,"
stationList = string.split(",")

#ksea
results = geo.Geocoder.reverse_geocode(float(stationList[5]),float(stationList[6]))
helper.dumpJSONtoFile("GeoLoc.json",results.data)

def getAddress(lat,lon):
    results = geo.Geocoder.reverse_geocode(lat,lon)
    return results.formatted_address
    

#####read in combined Station list and output to new file with google address at end
#1-load stations
stationList = []
inFile = open("missing-address.csv",'r')
try:
    reader = csv.reader(inFile)
    for row in reader:
        stationList.append(row)
finally:
    inFile.close()
    
#2-get address and output to csv
#NOTE: This is a workaround to collect most of data.  Cannot figure out how to handle unicode error.
#I have tried: http://stackoverflow.com/questions/9942594/unicodeencodeerror-ascii-codec-cant-encode-character-u-xa0-in-position-20
# & everything through example 4 here: https://pythonhosted.org/kitchen/unicode-frustrations.html
outFile = open('found-address.csv','w')
writer = csv.writer(outFile)
for station in stationList:
    try:    
        print "getting address for: " + station[4]
        results = geo.Geocoder.reverse_geocode(float(station[5]),float(station[6]))
        address = results.formatted_address
        #address = address.encode('utf8','replace')
        print station
        try:
            tempStation = station[:]
            tempStation.append(address)
            writer.writerow(tempStation)
        except:
            station.append("UTFERROR-Could Not Retrieve Address")
            print station
            print tempStation
            writer.writerow(station)            
    except Exception as err:
        print station[4]
        #print err
        station.append("Could Not Retrieve Address")
        print station
        writer.writerow(station)            


outFile.close()


def getTimeZone(latitude,longitude):
    api_key = "fill in"
    timestamp = time.time()
    api_response = requests.get('https://maps.googleapis.com/maps/api/timezone/json?location={0},{1}&timestamp={2}&key={3}'.format(latitude,longitude,timestamp,api_key))
    api_response_dict = api_response.json()
    return api_response_dict['rawOffset']
    

##get timezone from google
#1-load stations
stationList = []
inFile = open("no-time.csv",'r')
try:
    reader = csv.reader(inFile)
    for row in reader:
        stationList.append(row)
finally:
    inFile.close()
    
#get time and output to csv


api_key = "fill in"

outFile = open('with-time.csv','w')
writer = csv.writer(outFile)
for station in stationList:
    latitude  = float(station[5])
    longitude = float(station[6])
    timestamp = time.time()
    try:    
        print "getting timezone for: " + station[4]
        api_response = requests.get('https://maps.googleapis.com/maps/api/timezone/json?location={0},{1}&timestamp={2}&key={3}'.format(latitude,longitude,timestamp,api_key))
        api_response_dict = api_response.json()
        #address = address.encode('utf8','replace')
        try:
            tempStation = station[:]
            tempStation.append(api_response_dict['rawOffset'])
            writer.writerow(tempStation)
        except:
            station.append("UTFERROR-Could Not Retrieve Timezon")
            print station
            print tempStation
            writer.writerow(station)            
    except Exception as err:
        print station[4]
        #print err
        station.append("Could Not Retrieve Timezone")
        print station
        writer.writerow(station)            


outFile.close()

#create combined list
from wxtalk.db import dbfuncs
db = dbfuncs.Stations()

climFile = open('ClimMasterStationList.csv','r')
metarFile = open('MetarMasterList.csv','r')

outFile = open('CombinedMasterStationList.csv','w')

climateIDdict={}
climFile.readline()
for line in climFile:
    line = line.split(',')
    stationID = line[4]
    climateIDdict[stationID]=None


outputList = [] 
for line in metarFile:
    line = line.split(',')
    line = line[:7]
    lon = line[6]
    lat = line[5]
    nearestClimateStation = db.getStationList([lon,lat],maxStations = 1,stationTable = "climateStations")
    nearestID = nearestClimateStation[0][0]
    nearestDist = str(nearestClimateStation[0][1])
    stationID = line[4]
    print line
    print stationID
    if stationID in climateIDdict:
        line.append("True")
    else:
        line.append("False")
    
    line.append(nearestID)
    line.append(nearestDist)
    line.append('\n')
    outputList.append(line)

for list in outputList:
    outLine = ",".join(list)
    outFile.write(outLine)

       
climFile.close()
metarFile.close()
outFile.close()
