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
		

class ClimateReport(object):
	'''Climate Report (daily climate report for NWS climate station'''

	def __init__( self, month=None, year=None, utcdelta=None):
		"""Initialize climate report"""
		self.report_error = False					# report good/bad
		self.errors = []									# list of errors
		self.reportLines = []							# list to store original report lines from html file
																			# average sky cover total/total possible [0.0 - 1.0]
		self.avg_sky_cvg = {'AVERAGE SKY COVER' : 'NOT AVAILABLE'}							

		
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
			if re.search('The chosen WFO ID could not be found in the database', line):
				self.report_error = True
				self.errors.append({climStationID : officeID + " is wrong WFO office code"})
				return {climStationID : officeID + " is wrong WFO office code"}
			if re.search('Sorry, no records are currently available', line):
				self.report_error = True
				self.errors.append({climStationID : climStationID + " is wrong WFO climate station code"})
				return {climStationID : climStationID + " is wrong WFO climate station code"}
			if re.search('<h3>Climatological Report', line):
				goodReport = True
			if goodReport:
				reportLines.append(line.rstrip())
				self.reportLines.append(line.rstrip())
		return reportLines
		
	def getSkyCover(self, reportLines):
		"""
		Grab the average sky cover.
		 
		The following attributes are set/returned:
				sky cover         [average for day range 0.0-1.0]
		"""
		#TODO: Need to change default of 'NOT AVAILABLE' to 
		self.reportLines = reportLines
		for line in self.reportLines:
			if re.search('AVERAGE SKY COVER', line):
				startIdx = line.find('AVERAGE')
				lineList = line[startIdx:].split()
				if lineList[3] == 'MM':
					self.avg_sky_cvg = {'AVERAGE SKY COVER' : 'MISSING'}
				else:
					self.avg_sky_cvg =  {'AVERAGE SKY COVER' : convertToFloat(lineList[3])}
			#self.avg_sky_cvg =  {'AVERAGE SKY COVER' : 'NOT AVAILABLE'}			
 


