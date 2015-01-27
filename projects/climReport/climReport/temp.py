import re
def convertColumnVal(string):
	'''We want to convert string to float, MM to missing and keep everything else as string
	keep/store/return original string if exception is thrown'''
	string = string.strip()
	print string
	try:
		return float(string)
	except:
		if re.search('MM', string):
			return 'MISSING'
		elif re.search('AM', string) or re.search('PM', string):
			return string
		elif re.match('\d+R', string):
			return 'RECORD'
		else:
			return string + ' IS UNKNOWN VALUE'


#def getColumns(repHeader):	
repColumns = repHeader.split()[2:]
columnIdxs = []
for column in repColumns:
	startIdx = repHeader.find(column)
	columnIdxs.append(startIdx)

#def getColumnValues(repHeader):
i = 0
weatherCurrentLine = {}
while i < len(columnIdxs):
	rawValue = ''
	convertedValue = ''
	maxMin = ''
	if i == 0:
		maxMin = repValues [ : columnIdxs[i] ]
	if (i + 1) == len(columnIdxs):
		rawValue = repValues[ columnIdxs[i]: ]
		#print rawValue
		convertedValue = convertColumnVal(rawValue)
	else:
		rawValue = repValues[ columnIdxs[i]:columnIdxs[i + 1] ]
		#print rawValue
		convertedValue = convertColumnVal(rawValue)
	if convertedValue == 'RECORD':
		weatherCurrentLine['NEW RECORD'] = True
		recordVal = convertColumnVal(rawValue.split('R')[0])
		weatherCurrentLine[ repColumns[i] ] = recordVal
	else:
		weatherCurrentLine[ repColumns[i] ] = convertedValue
	i += 1		
	

print weatherCurrentLine	

	
repHeader = 'WEATHER ITEM   OBSERVED TIME   RECORD YEAR NORMAL DEPARTURE LAST'	
repValues = '  MAXIMUM         80    140 PM  85    1996  80      0       77'
repValues = '  MAXIMUM         80    140 PM  85    1996  80      0       77'

'WEATHER ITEM   OBSERVED TIME   RECORD YEAR NORMAL DEPARTURE LAST'	