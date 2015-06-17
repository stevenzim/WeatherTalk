#author: Steven Zimmerman
#created: 09-JUN-2015
#module to retrieve wx station information from weather db

from wxtalk import helper
import psycopg2
import sys
import os


import logging

# set up logging to file - see previous section for more details
#from: https://docs.python.org/2/howto/logging-cookbook.html
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename = os.path.join(helper.getProjectPath(),'wxtalk/errors/db.log'),
                    filemode='a')

logger1 = logging.getLogger('wxtalk.MetarReport')


class Connector(object):
    '''Simple connector to be reused in classes below'''
    def __init__(self,connectionParams = "dbname=weather user=steven password=steven"):
        self.conparams = connectionParams
        self.connection = psycopg2.connect(self.conparams) 
        self.cursor = self.connection.cursor()    

class MetarReport(object):
    '''
    usage:
    from db import dbfuncs
    '''
    def __init__(self):
        #establish db connection
        self.con = Connector()
        
    def retrieveMetarReport(self,datetimeStamp,metarStationID):
        '''Provided a datetime stamp and metar station ID. 
        This function returns a metar report from database that is closest to datetime for station'''
        #TODO: Consider if it is better to have a unique ID and return this?
        return 0
        
    def loadMetarReport(self,metarDict):
        '''
        pass in dictionary matching format produced by wxtalk.wxcollector.createMetarTable.getMetarDict(metarString)
        loads metar report if it exists
        if it exists already, then assume this is updated version --> delete existing, then create new record
        '''
        
        #throw error if data passed in is not a dict
        if type(metarDict) != type({}):
            raise Exception("This function expects a dictionary containing metar data")

        #inspired by http://stackoverflow.com/questions/29461933/insert-python-dictionary-using-psycopg2
        #convert keys to column names and then create string
        columns = metarDict.keys()
        columns_str = ", ".join(columns)
        #convert values to column names and then create string
        values = [metarDict[x] for x in columns]
        values_str_list = [str(value) for value in values]
        values_str = "\',\'".join(values_str_list)
        #create insert string
        sqlinsertstring = 'INSERT INTO weather.metar_report (' + columns_str + ')\
                                 VALUES (\'' + values_str + '\');'
                                                    

        #load station into db
        #if exception thrown, then record likely exists, therefore delete record and try again
        try:
            self.con.cursor.execute(sqlinsertstring)
            self.con.connection.commit()
        except psycopg2.IntegrityError as error:
            try:
                #restablish connection, try to delete existing record and then insert in new record
                self.con.cursor.close()
                self.con = Connector()
                sqldeletestring = 'DELETE FROM weather.metar_report\
                            WHERE ICAO_ID = \'' + metarDict['ICAO_ID'] + '\' AND observation_time = \'' + metarDict['observation_time'] + '\''
                self.con.cursor.execute(sqldeletestring)
                self.con.connection.commit()
                self.con.cursor.execute(sqlinsertstring)
                self.con.connection.commit()
            except Exception as error:
                # if it can't be deleted or inserted, do warn me so I can review the data
                # 23503 = FK violation in Postgre.  This is due to the occasional METAR report that is not loaded in metar master station list
                # We don't want these reports in our db so we can supress error logging
                if error.pgcode != 23503:
                    #TODO: fix error logging, currently it is logging way to much, sometimes FK error still logged
                    logger1.error('DB loadMetarReport: %s',  error)
                raise Exception("Record could not be deleted nor inserted.  Review original metar data, most likely a report that is not in master station list")       


class Stations(object):
    '''
    usage:
    from db import dbfuncs
    db = dbfuncs.Stations()
    db.getStationList([-75.,44.])
    
    returns [('KSLK', 48.312), ('KART', 51.219), ('KMSS', 64.681)]
    '''
    def __init__(self,connectionParams = "dbname=weather user=steven password=steven"):
        self.con = Connector()

    def getStationList(self,twitterCoords,maxStations = 3,stationTable = "metarStations"):
        '''
        Pass in a list of coordinates in [longitude,latitude] format
        Returns a list of tuples containing top 3 
        stationTable = default(metarStations) or climateStations
        '''
        #con = Connector()  #create connection obj
        stationCoordString = str(tuple(twitterCoords))
        print stationCoordString

        #sql statement to retrieve sorted list of stations with distances in statue miles
        sql = "SELECT ICAO_ID, name, latitude, longitude, location,\
               round((location <@> point" + stationCoordString + ")::numeric, 3) as miles \
        FROM weather." + stationTable + " \
        ORDER BY round((location <@> point" + stationCoordString + ")::numeric, 3) \
        limit " + str(maxStations) + ";" 
        
        
        listToReturn = []
        
        #get nearest station
        #error handling in the event that wrong point format thrown in
        try:
            self.con.cursor.execute(sql)
            listOfStations = self.con.cursor.fetchall()
        except:
            #restablish connection and throw exception error
            self.con.cursor.close()
            self.con = Connector()
            raise TypeError("Coordinate must be passed in as list/tuple format (lat,lon)")
        
        #build and return list of stations and distances    
        for record in listOfStations:
            stationID = record[0]
            stationDistance = record[-1].__float__()
            listToReturn.append([stationID,stationDistance])
        
        return listToReturn    



