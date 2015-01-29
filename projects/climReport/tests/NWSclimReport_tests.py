from nose.tools import *
from climReport import NWSclimReport as Climate
import os


def loadTestReport(fileName):
	'''Load test data'''
	testFilePath = "testData/"
	report = open(testFilePath + fileName, 'r')
	reportLines = []
	for line in report:
		reportLines.append(line.rstrip())	
	return reportLines

	
def test_stringToFloat():
	'''Verify try string to float is working'''
	assert_equal(Climate.convertToFloat("EIGHT") , 'EIGHT IS NOT A NUMBER' )
	assert_equal(Climate.convertToFloat("8") , 8.0 )
	
def test_get_report():
	'''Verify correct errors are returned if report is missing'''
	report = Climate.ClimateReport()
	assert_equal(report.getReport("see","SEA") , {"SEA" : "see is wrong WFO office code"})
	assert_equal(report.report_error , True)
	assert_equal(report.errors , [{"SEA" : "see is wrong WFO office code"}])
	assert_equal(report.getReport("sew","SEE") , {"SEE" : "SEE is wrong WFO climate station code"})


def test_sky():
	report = Climate.ClimateReport()
	
	report.getSkyCover(loadTestReport("testReport1.txt"))
	assert_equal(report.avg_sky_cvg , {'AVERAGE SKY COVER' : 0.7})
	
	report.getSkyCover(loadTestReport("testReport2.txt"))
	assert_equal(report.avg_sky_cvg , {'AVERAGE SKY COVER' : 'MISSING'})

def test_wind():
	report = Climate.ClimateReport()
	report.getWinds(loadTestReport("testReport1.txt"))
	assert_equal(report.winds , {'HIGHEST WIND SPEED' : 17.0 , 'HIGHEST GUST SPEED' : 21.0, 'AVERAGE WIND SPEED' : 5.8})

def test_temp():
	report = Climate.ClimateReport()
	report.getTemps(loadTestReport("testReport1.txt"))
	assert_equal(report.max_temps , {'OBSERVED' : 80.0, 'TIME' : '140 PM', 'RECORD' : 85.0, 'YEAR' : 1996.0 ,  'NORMAL' : 80.0 , 'DEPARTURE' : 0.0, 'LAST' : 77.0})
	assert_equal(report.min_temps , {'OBSERVED' : 71.0, 'TIME' : '527 AM', 'RECORD' : 55.0, 'YEAR' : 1969.0 ,  'NORMAL' : 66.0 , 'DEPARTURE' : 5.0, 'LAST' : 61.0})

	report = Climate.ClimateReport()
	report.getTemps(loadTestReport("testReport3.txt"))
	assert_equal(report.max_temps ,{'OBSERVED' : 61.0, 'NEW RECORD' : True, 'TIME' : '400 PM', 'RECORD' : 58.0, 'YEAR' : 2003.0 ,  'NORMAL' : 48.0 , 'DEPARTURE' : 13.0, 'LAST' : 47.0})

	
def test_precip():
	report = Climate.ClimateReport()
	report.getPrecipData(loadTestReport("testReport1.txt"))
	assert_equal(report.precipitation , {'OBSERVED' : 0.10, 'TIME' : '', 'RECORD' : 4.75, 'YEAR' : 1972.0 ,  'NORMAL' : 0.07 , 'DEPARTURE' : 0.03, 'LAST' : 0.00})

	report = Climate.ClimateReport()
	report.getPrecipData(loadTestReport("testReport4.txt"))
	assert_equal(report.snow , {'OBSERVED' : 22.1, 'NEW RECORD' : True, 'TIME' : '', 'RECORD' : 22.1, 'YEAR' : 2015.0 ,  'NORMAL' : 0.4 , 'DEPARTURE' : 21.7, 'LAST' : 0.0})
	
def test_output_dict():
	test = {'UUID': {'STATION': None,
									'TEMPERATURE': {'MAXIMUM': {},
																	'MINIMUM': {}},
									'PRECIPITATION': {'LIQUID': {},
																	'SNOWFALL': {}},
									'WINDS': {},
									'SKIES': {}}}
	report = Climate.ClimateReport()
	assert_equal(report.buildOutputDictionary(),test)
