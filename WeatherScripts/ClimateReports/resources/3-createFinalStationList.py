"""Script to create final list of stations that meet criter
	
	Written by: Steven Zimmerman
	Date: Jan 21st  2015

	
	Description: Given a file/list of all NWS stations with desired daily 
							climate reports and a file with all metar stations for USA.
							Create a master list of climate reporting stations that also have 
							a metar station.			

							Some manual post processing is necessary
	
	
	TODO:

	Usage:
	$ python 3-createFinalStationList.py
"""

oFile = open('finalStationsList.csv' ,'w')
climStationFile = open('ClimateStations-WithReportHeader.csv' ,'r')
climHeader = climStationFile.readline()  #header
for climStation in climStationFile:
	climStationData = climStation.split(',')
	PotentialICAO = climStationData[2] #this code represents a potential metar station, we only want climate reports that actually have a metar station
	metarFile = open('USA-metars.csv' ,'r')
	metarHeader = metarFile.readline()
	for metarStation in metarFile:
		metarStationData = metarStation.split(',')
		metarICAO = metarStationData[0]
		if PotentialICAO == metarICAO:
			print metarICAO
			oFile.write( "True," + climStationData[0] + "," + climStationData[1] + "," + climStationData[3] + "," + climStationData[4])
			oFile.write( "," + metarStationData[0] + "," + metarStationData[1] + "," + metarStationData[2] + "," + metarStationData[3] + '\n')
	metarFile.close()

			
oFile.close()
			
	