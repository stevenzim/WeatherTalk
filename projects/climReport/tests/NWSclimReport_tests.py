from nose.tools import *
from climReport import NWSclimReport as Climate
import os


def loadTestReport(fileName):
	testFilePath = "testData/"
	report = open(testFilePath + fileName, 'r')
	reportLines = []
	for line in report:
		reportLines.append(line.rstrip())	
	return reportLines

	
#OOP
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

