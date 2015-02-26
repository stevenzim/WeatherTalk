#!/usr/bin/env python
#
#  A python package for extracting reported daily climatology from the 
#	 US National Weather Service (NWS) daily climate report
# 
#	 These products are issued daily and provide information such as hi/lo temps
#  precip/snow totals, observed weather, total cloud cover, etc.
#
#  The NCDC http://www.ncdc.noaa.gov/cdo-web/datasets provides official climate data
#
#  These NWS daily climate reports are unofficial.  However, the reports are still very useful
#  1) They have derived products, such as average cloud cover, which are not easily available from NCDC
#  2) They are relevant for 0000 - 2359 local time, which is important if you want to know the highs and lows specific
#     to the relative time at the location.  WMO (World Meteorological Org) and NCDC data is reported in UTC, with max/mins
#			recorded in the 12Z - 12Z period.  As such, the NWS report is a much more relevant report to people living near the station
#
#  At the moment, all precip and temp values in this report are in inches and fahrenheit respectively, but could be easily convertedValue
#
#  This class has only been tested for the stations in MasterStationList provided in project 
#  The reports for all stations have different formats, this module attempts to handle the dynamic nature of these reports.  
#  There are additonal stations which produce reports not in MasterStationList, however they have been excluded
#  because they are not official WMO/ICAO/METAR stations
#
#  The most recent Climate report for a given station is available at the URL where officeID could be any 3 letter code for offices
#  that issue daily reports and climStationID is 3 letter code for actual station.  See MasterStationList for details
#  http://www.weather.gov/climate/getclimate.php?date=&wfo=' + officeID +'&sid='+ climStationID + '&pil=CLI&recent=yes'
#
# 
#  Copyright 2015  Steven Zimmerman
# 
"""
This module defines the National Weather Service climate report class.  
A Climate Report object represents the weather data deemed most important from the
daily NWS climate report.  A Google search for "NWS Daily Climate Report" will provide examples

SEE Example.py for usage

The code, tests and docs for this package were inspired by Tom Pollard's
metar package found at http://python-metar.sourceforge.net/

"""

__author__ = "Steven Zimmerman"

__email__ = "szimme@essex.ac.uk"

__version__ = "0.1"

__LICENSE__ = """
Copyright (c) 2015, 
All rights reserved.

Redistribution and use in source and binary forms, 
with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, 
this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, 
this list of conditions and the following disclaimer in the documentation 
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, T
HE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, 
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


import urllib
import os
import re
import datetime

def convertToFloat(string):
	'''We want to convert string to float, and 
	keep/store/return original string if exception is thrown'''
	try:
		return float(string)
	except:
		return  string + ' IS NOT A NUMBER'
		
# TODO: PERHAPS MERGE convertToFloat and convertColumnVal???
def convertColumnVal(string):
	'''We want to convert string to float, MM to missing and keep everything else as string
	keep/store/return original string if exception is thrown'''
	string = string.strip()
	try:
		return float(string)
	except:
		if re.search('MM', string):
			return 'MISSING'
		elif re.search('AM', string) or re.search('PM', string):
			return string
		elif re.match('\d+R', string) or re.match('\d+.\d+R', string) or re.match('\d+.\d+ R', string):
			return 'RECORD'
		elif re.match('', string):
			return ''
		else:
			return string + ' IS UNKNOWN VALUE'		

class ClimateReport(object):
	'''Climate Report (daily climate report for NWS climate station'''

	def __init__( self, month=None, year=None, utcdelta=None):
		"""Initialize climate report"""
		#global report vars
		self.report_error = False					# report good/bad
		self.errors = []									# list of errors
		self.reportLines = []							# list to store original report lines from html file
		self.reportColumns = []						# stores variable string with available column names
		self.columnIdxs = []							# stores starting index of each column name

		#station variables
		self.uuid = None									# concatenation of ICAO + YYYYMMDD  There should never be more than one report for each ICAO + DATE combo
		self.valid_date = None						# date for which the report covers
		self.report_station_id = None			# 3 or 4 letter code used by NWS usually same as ICAO
		self.ICAO = None								# 4 letter ICAO identifier
		self.station_full_name = None			# full name of staion, usually city/airport
		self.station_timezone = None 		  # 3 letter timezone for station
		self.geo_point = None							# lat/lon of station			
		
		#extracted daily climate weather report vals
		self.avg_sky_cvg = {}		          # average sky cover total/total possible [0.0 - 1.0]	
		self.winds = {}										# max speed/max gust/avg wind for day in mph
		self.max_temps = {}        				# max temp data for report
		self.min_temps = {}          			# min temp data for report
		self.precipitation = {}						# precip data for report --> Melted precipitation
		self.snow = {}									  # snow data for report	
		self.observations = []						# list of all observed weather conditions
		self.sun = {}											# sunrise/sunset data for station  TODO: Consider if total minutes should be calculated
		
		#self.code = metarcode              # original METAR code
		self.type = 'METAR'                # METAR (routine) or SPECI (special)
		self.mod = "AUTO"                  # AUTO (automatic) or COR (corrected)
		self.station_id = None             # 4-character ICAO station code
		self.time = None                   # observation time [datetime]
		self.cycle = None                  # observation cycle (0-23) [int]
		self.wind_dir = None               # wind direction [direction]

		# self._now = datetime.datetime.utcnow()
		# if utcdelta:
				# self._utcdelta = utcdelta
		# else:
				# self._utcdelta = datetime.datetime.now() - self._now

		# self._month = month
		# self._year = year
		


	def setColumnNames(self, reportHeader):	
		'''
		Gets the column names from the header string.  These column names represent the types of values the report contains
		e.g. OBSERVATION RECORD TIME DEPARTURE.
		However, this function is required because not all reports provide the same values.
		This is a dynamic approach to the issue.
		'''
		self.reportColumns = reportHeader.split()[2:]
		columnIdxs = []
		for column in self.reportColumns:
			startIdx = reportHeader.find(column)
			columnIdxs.append(startIdx)
		self.columnIdxs = columnIdxs
		
	def getRowValues(self, rowString):
		'''
		Generic function to handle values found in the Temperature,
		Preciptiation and Snowfall sections.   Takes a line with raw Data
		e.g. "  MAXIMUM         80    140 PM  85    1996  80      0       77"
		and returns a dictionary combined with corresponding header information
		e.g. {'OBSERVED' : 71.0, 'TIME' : '527 AM', 'RECORD' : 66.0, 'YEAR' : 1969 ,  'NORMAL' : 80 , 'DEPARTURE' : 5, 'LAST' : 61}
		'''
		if self.reportColumns == []:
			for line in self.reportLines:
				if re.search('WEATHER ITEM', line):
					self.setColumnNames(line)
		
		i = 0
		weatherCurrentLine = {}
		while i < len(self.columnIdxs):
			rawValue = ''
			convertedValue = ''
			maxMin = ''
			if i == 0:
				maxMin = rowString [ : self.columnIdxs[i] ]
			if (i + 1) == len(self.columnIdxs):
				rawValue = rowString[ self.columnIdxs[i]: ]
				convertedValue = convertColumnVal(rawValue)
			else:
				rawValue = rowString[ self.columnIdxs[i]: self.columnIdxs[i + 1] ]
				convertedValue = convertColumnVal(rawValue)
			if convertedValue == 'RECORD':
				weatherCurrentLine['NEW RECORD'] = True
				recordVal = convertColumnVal(rawValue.split('R')[0])
				weatherCurrentLine[ self.reportColumns[i] ] = recordVal
			else:
				weatherCurrentLine[ self.reportColumns[i] ] = convertedValue
			i += 1
		return weatherCurrentLine

	def getReport(self, officeID, climStationID):
		'''
		 Provided an NWS office ID e.g. SEW = seattle and 
		 climStationID e.g. OLM = Olympia.  
		
		 Returns/sets the list attribute [reportLines]
		
		 Will retrieve the html daily climate report for the specified clim station
		 NOTE: though climate reports are produced by one NWS office for each climStationID
					 Climate reports can be retrieved for any valid officeID. i.e.  the report for
					 OLM can be retrieved with SEW(the issuing office for OLM) but also via any other
					 NWS office that produces daily reports (e.g. BOX = Boston)
		 If the report is available, the raw climate data is loaded into a list for
		 additional processing
		 
		'''
		#TODO: change from climStationID to ICAO.  Need to add ICAO paramater to function
		self.ICAO = climStationID
		goodReport = False
		reportLines = []
		urllib.urlretrieve ('http://www.weather.gov/climate/getclimate.php?date=&wfo=' + officeID +'&sid='+ climStationID + '&pil=CLI&recent=yes',"tempDaily.report")
		report = open("tempDaily.report" , 'r')
		for line in report:
			#problems with report
			if re.search('The chosen WFO ID could not be found in the database', line):
				self.report_error = True
				self.errors.append({climStationID : officeID + " is wrong WFO office code"})
				return {climStationID : officeID + " is wrong WFO office code"}
			if re.search('Sorry, no records are currently available', line):
				self.report_error = True
				self.errors.append({climStationID : climStationID + " is wrong WFO climate station code"})
				return {climStationID : climStationID + " is wrong WFO climate station code"}
			
			#report is good
			if re.search('<h3>Climatological Report', line):
				goodReport = True
			if goodReport:
				#get column Names and main report lines  and store to lists
				if re.search('WEATHER ITEM', line):
					self.setColumnNames(line)
				reportLines.append(line.rstrip())
				self.reportLines.append(line.rstrip())
		return reportLines

		
 	def getTemps(self, reportLines = None):
		"""
		Grab the temperature data.
		 
		Some or all of following attributes are set/returned:
		MAX/MIN TEMPS        {'OBSERVED' : 80.0, 'TIME' : '140 PM', 'RECORD' : 85.0, 'YEAR' : 1996 ,  'NORMAL' : 80 , 'DEPARTURE' : 0, 'LAST' : 77}
		
		Each report could have different types i.e. sometimes TIME is reported, other times it is not
		Also, an 'R' Next to observed temp is indicator that record has a occured and a field denoting New Record is created
		"""

		tempsToFind = ['MAXIMUM', 'MINIMUM']
		correctReportSection = False
		if reportLines != None:
			self.reportLines = reportLines
		for temps in tempsToFind:
			for line in self.reportLines:
				if re.search('TEMPERATURE',line):
					correctReportSection = True
				if re.search('PRECIPITATION',line):
					#break out of loop, report section is complete
					break
				if re.search(temps, line):
					convertedValues = self.getRowValues(line)
					if temps == 'MAXIMUM':
						self.max_temps = convertedValues
						#print convertedValues
						#print line
					if temps == 'MINIMUM':
						self.min_temps = convertedValues
		if self.max_temps == {}:
			self.max_temps = {'MAXIMUM' : 'NOT AVAILABLE'}
		if self.min_temps == {}:
			self.min_temps = {'MINIMUM' : 'NOT AVAILABLE'}

 	def getPrecipData(self, reportLines = None):
		"""
		Grab the precipitation data.
		
		gets the liquid precipitation values and the snow values if they exist.
		Denotes records if one was recorded

		"""
		precipSection = False
		snowSection = False
		if reportLines != None:
			self.reportLines = reportLines
		for line in self.reportLines:
			if re.search('PRECIPITATION',line):
				precipSection = True
			if re.search('SNOWFALL',line):
				snowSection = True
			if re.search('DEGREE DAYS',line):
				#break out of loop, report section is complete
				break
			if re.search('YESTERDAY', line) or re.search('TODAY', line):
				convertedValues = self.getRowValues(line)
				if precipSection == True and snowSection == False:
					self.precipitation = convertedValues
				if precipSection == True and snowSection == True:
					self.snow = convertedValues
		if self.precipitation == {}:
			self.precipitation = {'PRECIPITATION' : 'NOT AVAILABLE'}
		if self.snow == {}:
			self.snow = {'SNOWFALL' : 'NOT AVAILABLE'}
		
	def getSkyCover(self, reportLines = None):
		"""
		Grab the average sky cover.
		 
		The following attributes are set/returned:
				sky cover         {'AVERAGE SKY COVER' : 0.0-1.0}
		"""
		self.avg_sky_cvg =  {'AVERAGE SKY COVER' : 'NOT AVAILABLE'}
		if reportLines != None:
			self.reportLines = reportLines
		for line in self.reportLines:
			if re.search('AVERAGE SKY COVER', line):
				startIdx = line.find('AVERAGE')
				lineList = line[startIdx:].split()
				if lineList[3] == 'MM':
					self.avg_sky_cvg = {'AVERAGE SKY COVER' : 'MISSING'}
				else:
					self.avg_sky_cvg =  {'AVERAGE SKY COVER' : convertToFloat(lineList[3])}
		
 	def getWinds(self, reportLines = None):
		"""
		Grab the wind data.
		 
		Some or all of following attributes are set/returned:
		WINDS         {'HIGHEST WIND SPEED' : 17.0 , 'HIGHEST GUST SPEED' : 21.0, 'AVERAGE WIND SPEED' : 5.8}
		"""
		windsToFind = ['HIGHEST WIND SPEED', 'HIGHEST GUST SPEED' , 'AVERAGE WIND SPEED']
		if reportLines != None:
			self.reportLines = reportLines
		for wind in windsToFind:
			for line in self.reportLines:
				if re.search(wind, line):
					startIdx = line.find(wind)
					lineList = line[startIdx:].split()
					if lineList[3] == 'MM':
						self.winds[wind] = 'MISSING'
					else:
						self.winds[wind] = convertToFloat(lineList[3])
		if self.winds == {}:
			self.winds = {'WINDS' : 'NOT AVAILABLE'} 
			
	def getWxObs(self, reportLines = None):
		'''
		Grabs the observed weather conditions from report and puts them in a list
		observations = ['RAIN','LIGHT RAIN']
		'''
		correctReportSection = False
		if reportLines != None:
			self.reportLines = reportLines
		for line in self.reportLines:
			if re.search('THE FOLLOWING WEATHER',line):
				correctReportSection = True
				continue
			if correctReportSection == True and line.strip() =='':
				#break out of loop, report section is complete
				break
			if correctReportSection == True:
				self.observations.append(line.strip())
		if self.observations == []:
			self.observations = ['OBSERVATIONS MISSING']
	
	def getSunRiseSet(self, reportLines = None):
		'''
		Grabs the sunrise and sunset for the current day of report (note the report 
		gives weather for previous day). At most, there will be an error of 4 minutes,
		greatest error occurs on first day of Spring/Autumn, smallest error on 
		first day of Winter/Summer
		'''
		self.sun = {'SUNRISE' : 'MISSING', 'SUNSET' : 'MISSING'}
		correctReportSection = False
		if reportLines != None:
			self.reportLines = reportLines
		for line in self.reportLines:
			if re.search('SUNRISE AND SUNSET',line):
				correctReportSection = True
				continue
			if correctReportSection == True and re.search('SUNRISE',line):
				#grab and store sunrise/sunset information break out of loop, 
				#report section is now complete
				self.sun = {'SUNRISE' : line[29:38].strip(), 'SUNSET' : line[51:60].strip()}
				break



	def buildOutputDictionary(self):
		'''Build output dictionary'''
		#TODO: add in all station details
		dictToReturn = {'UUID': {'STATION': self.ICAO,
														'TEMPERATURE': {'MAXIMUM': self.max_temps,
																						'MINIMUM': self.min_temps},
														'PRECIPITATION': {'LIQUID': self.precipitation,
																						'SNOWFALL': self.snow},
														'WINDS': self.winds,
														'SKIES': self.avg_sky_cvg,
														'OBSERVATIONS': self.observations,
														'SUN' : self.sun}}	
		return dictToReturn
		



