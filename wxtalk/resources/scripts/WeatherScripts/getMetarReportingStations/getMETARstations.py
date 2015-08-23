#Script to produce dictionary of active metar stations based on a small collection of live reports and list provided by NCAR

from wxtalk import helper

pathToData = 'data/'
stationDict = {}  #{'stationID':countOfReports}
nsdcDict = {}
NCARdict = {}
files = helper.getListOfFiles(pathToData)

#load nsd data
nsdcFile = open("nsd_cccc.txt",'r')
for line in nsdcFile:
    line = line.replace(',',"")
    station = line.split(';')
    nsdcDict[station[0]] = station[3]

nsdcFile.close()


#load ncar/metar data
inFile = open('NCARstations.txt','r')
for line in inFile:
    stationName = line[:19].strip()
    stationID = line[20:24]
    stationActive = line[62:63]
    if stationID[0] != 'K':
            continue
    if stationActive != 'X':
            continue
    NCARdict[stationID] = stationName

inFile.close()

#Build dictionary for output
def updateDict(stationID,lat,lon):
    try:
        try:
            stationDict[stationID] = (float(lat),float(lon),NCARdict[stationID])
        except:
            try:
                stationDict[stationID] = (float(lat),float(lon),nsdcDict[stationID])
            except:
                stationDict[stationID] = (float(lat),float(lon),"No station name provided by NCAR/nsdc")
    except:
        pass


#iterate over weather report files, stations in these files are active.  We also want the lat/lon from these files
for file in files:
    inFile = open(pathToData + file, 'r')
    inFile.readline()
    inFile.readline()
    inFile.readline()
    inFile.readline()
    inFile.readline()
    inFile.readline()
    for line in inFile:
        report = line.split(',')
        stationID = report[1]
        try:
            if float(report[3]) > 90.  or (report[3]) < 0.:
                continue
            if float(report[4]) > -60.  or (report[4]) < -180.:
                continue
            if stationID[0] == 'K':
                print stationID
                updateDict(stationID,report[3],report[4])
        except:
            continue

        


#dump metar dictionary to json        
helper.dumpJSONtoFile('metarStations.json',stationDict)


#dump out metar stations to csv file
outFile = open('MetarMasterList.csv','w')
for key in stationDict:
    vals = stationDict[key]
    stringToWrite = "col0,col1," + vals[2] +",col3,"+key +","+str(vals[0])+","+str(vals[1])+",\n"
    outFile.write(stringToWrite)


outFile.close()



#build wxstring list
files = helper.getListOfFiles("30list/")
wxDict = {}
for file in files:
    inFile = open("30list/" + file, 'r')
    print file
    for line in inFile:
            report = line.split(',')
            wxString = report[11]
            wxDict[wxString] = None

oFile = open("wxStringList.txt",'w')
for key in wxDict:
    oFile.write(key + "\n")

oFile.close()
    

#clean up metar
#remove dupes
#dump to new csv file
#a prototype to quickly get rid of duplicate metars
files = helper.getListOfFiles("consec/")
files.sort()
metarDict = {}
for file in files:
    inFile = open("consec/" + file, 'r')
    print file
    for line in inFile:
            report = line.split(',')
            key = report[0]+report[1]
            metarDict[key] = line

oFile = open("MetarDupesRemoved.csv",'w')
for key in metarDict:
    oFile.write(metarDict[key])

oFile.close()

