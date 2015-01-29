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

		#extracted daily climate report vals
		self.avg_sky_cvg = {}		          # average sky cover total/total possible [0.0 - 1.0]	
		self.winds = {}										# max speed/max gust/avg wind for day in mph
		self.max_temps = {}        				# max temp data for report
		self.min_temps = {}          			# min temp data for report
		self.precipitation = {}									# precip data for report
		self.snow = {}									  # snow data for report	

		
		#self.code = metarcode              # original METAR code
		self.type = 'METAR'                # METAR (routine) or SPECI (special)
		self.mod = "AUTO"                  # AUTO (automatic) or COR (corrected)
		self.station_id = None             # 4-character ICAO station code
		self.time = None                   # observation time [datetime]
		self.cycle = None                  # observation cycle (0-23) [int]
		self.wind_dir = None               # wind direction [direction]
		self.wind_speed = None             # wind speed [speed]
		self.wind_gust = None              # wind gust speed [speed]
		self.wind_dir_from = None          # beginning of range for win dir [direction]
		self.wind_dir_to = None            # end of range for wind dir [direction]
		self.vis = None                    # visibility [distance]
		self.vis_dir = None                # visibility direction [direction]
		self.max_vis = None                # visibility [distance]
		self.max_vis_dir = None            # visibility direction [direction]
		self.temp = None                   # temperature (C) [temperature]
		self.dewpt = None                  # dew point (C) [temperature]
		self.press = None                  # barometric pressure [pressure]
		self.runway = []                   # runway visibility (list of tuples)
		self.weather = []                  # present weather (list of tuples)
		self.recent = []                   # recent weather (list of tuples)
		self.sky = []                      # sky conditions (list of tuples)
		self.windshear = []                # runways w/ wind shear (list of strings)
		self.wind_speed_peak = None        # peak wind speed in last hour
		self.wind_dir_peak = None          # direction of peak wind speed in last hour
		self.peak_wind_time = None         # time of peak wind observation [datetime]
		self.wind_shift_time = None        # time of wind shift [datetime]
		self.max_temp_6hr = None           # max temp in last 6 hours
		self.min_temp_6hr = None           # min temp in last 6 hours
		self.max_temp_24hr = None          # max temp in last 24 hours
		self.min_temp_24hr = None          # min temp in last 24 hours
		self.press_sea_level = None        # sea-level pressure
		self.precip_1hr = None             # precipitation over the last hour
		self.precip_3hr = None             # precipitation over the last 3 hours
		self.precip_6hr = None             # precipitation over the last 6 hours
		self.precip_24hr = None            # precipitation over the last 24 hours
		self._trend = False                # trend groups present (bool)
		self._trend_groups = []            # trend forecast groups
		self._remarks = []                 # remarks (list of strings)
		self._unparsed_groups = []
		self._unparsed_remarks = []

		# self._now = datetime.datetime.utcnow()
		# if utcdelta:
				# self._utcdelta = utcdelta
		# else:
				# self._utcdelta = datetime.datetime.now() - self._now

		# self._month = month
		# self._year = year
		


	def setColumnNames(self, reportHeader):	
		self.reportColumns = reportHeader.split()[2:]
		print "hello"
		print reportHeader
		columnIdxs = []
		for column in self.reportColumns:
			startIdx = reportHeader.find(column)
			columnIdxs.append(startIdx)
		self.columnIdxs = columnIdxs
		
	def getRowValues(self, rowString):
		'''Generic function to handle values found in the Temperature,
		Preciptiation and Snowfall sections.   Takes a line with raw Data
		e.g. "  MAXIMUM         80    140 PM  85    1996  80      0       77"
		and returns a dictionary combined with corresponding header information
		e.g. {'OBSERVED' : 71.0, 'TIME' : '527 AM', 'RECORD' : 66.0, 'YEAR' : 1969 ,  'NORMAL' : 80 , 'DEPARTURE' : 5, 'LAST' : 61}'''
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
		#print self.columnIdxs
		#print rowString
		#print weatherCurrentLine
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
		Grab the precipitationdata data.
		 

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
					print line
					print convertedValues
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


