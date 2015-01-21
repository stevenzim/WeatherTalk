"""Script to determine header information from weather report for each
		NWS climate reporting station
	
	Written by: Steven Zimmerman
	Date: Jan 21st  2015

	
	Description: Given a file/list of all NWS stations with daily reports.  This
							script will pull the report header for each station.  This is 
							necessary to determine what station reports the desired values.
							Each station must report observed and normal values (ideally departure too).  
							All other stations will be removed from final list.
							
							After running this script it is easiest to manually remove stations
							that do not meet criteria.	
		
	Resources (very helpful in creation of script): 
	#http://www.weather.gov
	
	TODO:

	Usage:
	$ python getStationHeaders.py
"""

oFile = open('ClimateStations-WithReportHeader.csv' ,'w')
iFile = open('climReportStationList.csv' ,'r')
iFile.readline()  #header
for line in iFile:
	temperatureSection = 0
	stationData = line.split(',')
	stationOfficeCode = stationData[2] #office related to station
	stationName = stationData[3]  #station name e.g. city
	stationCode = stationData[4]  #station id
	urllib.urlretrieve ('http://www.weather.gov/climate/getclimate.php?date=&wfo=SEW&sid='+ stationCode + '&pil=CLI&recent=yes',"tempDaily.report")
	htmlFile = open('tempDaily.report' ,'r')
	oFile.write(stationOfficeCode + ',' + stationCode + ',' + stationName +  ',')
	for htmlLine in htmlFile:
		if re.search('WEATHER ITEM',htmlLine):
			oFile.write(htmlLine)
			print stationOfficeCode
			print stationName

			
oFile.close()
			
			