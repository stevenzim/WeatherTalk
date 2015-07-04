#author: Steven Zimmerman
#created: 09-JUN-2015
#modified 01-JUL-2015 For Climate Reports
#modified 04-JUL-2015 For Tweets
#module to retrieve wx station information from weather db
#TODO: Refactor code in load tweets and load metar, the dictionary function to build insert strings could be changed to helper fcn
#TODO: Create a more elegant solution for metar and climate classes, lots of this stuff could be combined.  It works, however

from wxtalk import helper
import psycopg2
import sys
import os


import logging

# set up logging to file - see previous section for more details
#from: https://docs.python.org/2/howto/logging-cookbook.html
#TODO: If time, look into this more
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

class ClimateReport(object):
    '''
    usage:
    from db import dbfuncs
    see examples in examples/db
    '''
    def __init__(self):
        #establish db connection
        self.con = Connector()
        
    def retrieveClimateReport(self,climateStationID,datetimeStamp,sqlSelect = ' * ',limit = '2'):
        '''Provided a datetime stamp and climate station ID. 
        This function returns the most recent climate report from database relative to the station/datetime provided
        By default, all fields are returned, however a simple change to SELECT statement will alter results
        e.g. weather.uid will return on the uid field
        DATETIME must be in acceptable ansi format
        Returns a sorted list of reports, most recent first, default limit = 2'''
        sqlstring = 'SELECT '+ sqlSelect +'\
                    FROM weather.climate\
                    WHERE icao_id = \''+ climateStationID +'\'  AND report_start_datetime <= \''+ datetimeStamp +'\'::timestamp  AND\
                                    report_start_datetime > (\''+ datetimeStamp +'\'::timestamp - interval \'48 hours\')::timestamp\
                    ORDER BY report_start_datetime DESC LIMIT '+ limit +';'
        try:
            self.con.cursor.execute(sqlstring)
            return self.con.cursor.fetchall()
        except Exception as error:
            #restablish connection and record error
            self.con.cursor.close()
            self.con = Connector()
            logger1.error('DB retrieveClimateReport: %s',  error)
            raise Exception('Report could not be retrieved, perhaps wrong datestamp, stationID or sqlselect statemnt')

    def loadClimateReport(self,climateDict):
        '''
        pass in dictionary matching format produced by wxtalk.wxcollector.processclimate.py setClimateDict(climateDict)
        loads climate report into db if it doesnt exist
        if it exists already, then assume this is updated version --> delete existing, then create new record
        '''
        
        #throw error if data passed in is not a dict
        if type(climateDict) != type({}):
            raise Exception("This function expects a dictionary containing climate data")

        #inspired by http://stackoverflow.com/questions/29461933/insert-python-dictionary-using-psycopg2
        #convert keys to column names and then create string
        columns = climateDict.keys()
        columns_str = ", ".join(columns)
        #convert values to column names and then create string
        values = [climateDict[x] for x in columns]
        values_str_list = [str(value) for value in values]
        values_str = "\',\'".join(values_str_list)
        #create insert string
        sqlinsertstring = 'INSERT INTO weather.climate (' + columns_str + ')\
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
                sqldeletestring = 'DELETE FROM weather.climate\
                            WHERE icao_id = \'' + climateDict['icao_id'] + '\' AND observation_time = \'' + climateDict['observation_time'] + '\''
                self.con.cursor.execute(sqldeletestring)
                self.con.connection.commit()
                self.con.cursor.execute(sqlinsertstring)
                self.con.connection.commit()
            except Exception as error:
                raise Exception("Record could not be deleted nor inserted.  Review original climate data, most likely a report that is not in master station list")     



class MetarReport(object):
    '''
    usage:
    from db import dbfuncs
    '''
    def __init__(self):
        #establish db connection
        self.con = Connector()
        
    def retrieveMetarReport(self,metarStationID,datetimeStamp,sqlSelect = ' * ',limit = '1'):
        '''Provided a datetime stamp and metar station ID. 
        This function returns the most recent metar report from database relative to the station provided
        By default, all fields are returned, however a simple change to SELECT statement will alter results
        e.g. weather.uid will return on the uid field
        DATETIME must be in acceptable ansi format
        Returns a sorted list of reports, most recent first, default limit = 1'''
        #TODO: Would this query be more efficient with indexing on station ID and observation time? 
        #       What is the best way to index? 
        #       Perhaps it is already indexed automatically because they are PK?
        #TODO: Consider adding criteria to WHERE clause -->  timedelta <= threshold e.g. 3600 seconds
#        sqlstring = 'SELECT '+ sqlSelect +'\
#                    FROM weather.metar_report\
#                    WHERE ICAO_ID = \''+ metarStationID +'\'  AND observation_time <= \''+ datetimeStamp +'\'::timestamp\
#                    ORDER BY observation_time DESC LIMIT '+ limit +';'
        sqlstring = 'SELECT '+ sqlSelect +'\
                    FROM weather.metar\
                    WHERE icao_id = \''+ metarStationID +'\'  AND observation_time <= \''+ datetimeStamp +'\'::timestamp  AND\
                                    observation_time > (\''+ datetimeStamp +'\'::timestamp - interval \'2 hours\')::timestamp\
                    ORDER BY observation_time DESC LIMIT '+ limit +';'
        try:
            self.con.cursor.execute(sqlstring)
            return self.con.cursor.fetchall()
        except Exception as error:
            #restablish connection and record error
            self.con.cursor.close()
            self.con = Connector()
            logger1.error('DB retrieveMetarReport: %s',  error)
            raise Exception('Report could not be retrieved, perhaps wrong datestamp, stationID or sqlselect statemnt')

    def loadMetarReport(self,metarDict):
        '''
        pass in dictionary matching format produced by wxtalk.wxcollector.createMetarTable.getMetarDict(metarString)
        loads metar report if it doesnt exist
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
        sqlinsertstring = 'INSERT INTO weather.metar (' + columns_str + ')\
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
                sqldeletestring = 'DELETE FROM weather.metar\
                            WHERE icao_id = \'' + metarDict['icao_id'] + '\' AND observation_time = \'' + metarDict['observation_time'] + '\''
                self.con.cursor.execute(sqldeletestring)
                self.con.connection.commit()
                self.con.cursor.execute(sqlinsertstring)
                self.con.connection.commit()
            except Exception as error:
                # if it can't be deleted or inserted, do warn me so I can review the data
                # 23503 = FK violation in Postgre.  This is due to the occasional METAR report that is not loaded in metar master station list
                # We don't want these reports in our db so we can supress error logging
                #if error.pgcode != 23503:
                    #TODO: fix error logging, currently it is logging way to much, sometimes FK error still logged
                #logger1.error('DB loadMetarReport: %s',  error)
                    #logger1.error('DB loadMetarReport: %s',  error.pgcode)
                raise Exception("Record could not be deleted nor inserted.  Review original metar data, most likely a report that is not in master station list")     
        
#    def loadMetarReport(self,metarDict):
#        '''
#        pass in dictionary matching format produced by wxtalk.wxcollector.createMetarTable.getMetarDict(metarString)
#        loads metar report if it doesnt exist
#        if it exists already, then assume this is updated version --> delete existing, then create new record
#        '''
#        
#        #throw error if data passed in is not a dict
#        if type(metarDict) != type({}):
#            raise Exception("This function expects a dictionary containing metar data")

#        #inspired by http://stackoverflow.com/questions/29461933/insert-python-dictionary-using-psycopg2
#        #convert keys to column names and then create string
#        columns = metarDict.keys()
#        columns_str = ", ".join(columns)
#        #convert values to column names and then create string
#        values = [metarDict[x] for x in columns]
#        values_str_list = [str(value) for value in values]
#        values_str = "\',\'".join(values_str_list)
#        #create insert string
#        sqlinsertstring = 'INSERT INTO weather.metar_report (' + columns_str + ')\
#                                 VALUES (\'' + values_str + '\');'
#                                                    

#        #load station into db
#        #if exception thrown, then record likely exists, therefore delete record and try again
#        try:
#            self.con.cursor.execute(sqlinsertstring)
#            self.con.connection.commit()
#        except psycopg2.IntegrityError as error:
#            try:
#                #restablish connection, try to delete existing record and then insert in new record
#                self.con.cursor.close()
#                self.con = Connector()
#                sqldeletestring = 'DELETE FROM weather.metar_report\
#                            WHERE ICAO_ID = \'' + metarDict['ICAO_ID'] + '\' AND observation_time = \'' + metarDict['observation_time'] + '\''
#                self.con.cursor.execute(sqldeletestring)
#                self.con.connection.commit()
#                self.con.cursor.execute(sqlinsertstring)
#                self.con.connection.commit()
#            except Exception as error:
#                # if it can't be deleted or inserted, do warn me so I can review the data
#                # 23503 = FK violation in Postgre.  This is due to the occasional METAR report that is not loaded in metar master station list
#                # We don't want these reports in our db so we can supress error logging
#                if error.pgcode != 23503:
#                    #TODO: fix error logging, currently it is logging way to much, sometimes FK error still logged
#                    logger1.error('DB loadMetarReport: %s',  error)
#                    logger1.error('DB loadMetarReport: %s',  error.pgcode)
#                raise Exception("Record could not be deleted nor inserted.  Review original metar data, most likely a report that is not in master station list")       




class Stations(object):
    '''
    usage:
    from wxtalk.db import dbfuncs
    db = dbfuncs.Stations()
    db.getStationList([-75.,44.])
    
    returns [('KSLK', 48.312), ('KART', 51.219), ('KMSS', 64.681)]
    '''
    def __init__(self,connectionParams = "dbname=weather user=steven password=steven"):
        self.con = Connector()

    def getStationList(self,twitterCoords,maxStations = 3,stationTable = "stations",climateStationBool = False):
        '''
        Pass in a list of coordinates in [longitude,latitude] format
        Returns a list of tuples containing top 3 
        stationTable = default(metarStations) or climateStations
        '''
        #con = Connector()  #create connection obj
        stationCoordString = str(tuple(twitterCoords))

        #sql statement to retrieve sorted list of stations with distances in statue miles
        sql = ''
        if climateStationBool:
            sql = "SELECT icao_id, latitude, longitude, lat_lon_point,climate_station,\
                   round((lat_lon_point <@> point" + stationCoordString + ")::numeric, 3) as miles \
            FROM weather." + stationTable + " \
            WHERE climate_station = " + str(climateStationBool) + " \
            ORDER BY round((lat_lon_point <@> point" + stationCoordString + ")::numeric, 3) \
            limit " + str(maxStations) + ";" 
        else:
            sql = "SELECT icao_id, latitude, longitude, lat_lon_point,climate_station,\
                   round((lat_lon_point <@> point" + stationCoordString + ")::numeric, 3) as miles \
            FROM weather." + stationTable + " \
            ORDER BY round((lat_lon_point <@> point" + stationCoordString + ")::numeric, 3) \
            limit " + str(maxStations) + ";" 
        

        
        listToReturn = []
        
        #get nearest station
        #error handling in the event that wrong point format thrown in
        try:
            self.con.cursor.execute(sql)
            listOfStations = self.con.cursor.fetchall()
        except Exception as err:
            #restablish connection and throw exception error
            self.con.cursor.close()
            self.con = Connector()
            raise TypeError("Coordinate must be passed in as list/tuple format (lat,lon)")
        
        #build and return list of stations and distances    
        for record in listOfStations:
            #print record
            stationID = record[0]
            climateBool = record[-2]
            stationDistance = record[-1].__float__()
            listToReturn.append([stationID,stationDistance,climateBool])
        
        return listToReturn  


#    def getStationListOld(self,twitterCoords,maxStations = 3,stationTable = "metarStations"):
#        '''
#        Pass in a list of coordinates in [longitude,latitude] format
#        Returns a list of tuples containing top 3 
#        stationTable = default(metarStations) or climateStations
#        '''
#        #con = Connector()  #create connection obj
#        stationCoordString = str(tuple(twitterCoords))
#        #print stationCoordString

#        #sql statement to retrieve sorted list of stations with distances in statue miles
#        sql = "SELECT ICAO_ID, name, latitude, longitude, location,\
#               round((location <@> point" + stationCoordString + ")::numeric, 3) as miles \
#        FROM weather." + stationTable + " \
#        ORDER BY round((location <@> point" + stationCoordString + ")::numeric, 3) \
#        limit " + str(maxStations) + ";" 
#        
#        
#        listToReturn = []
#        
#        #get nearest station
#        #error handling in the event that wrong point format thrown in
#        try:
#            self.con.cursor.execute(sql)
#            listOfStations = self.con.cursor.fetchall()
#        except:
#            #restablish connection and throw exception error
#            self.con.cursor.close()
#            self.con = Connector()
#            raise TypeError("Coordinate must be passed in as list/tuple format (lat,lon)")
#        
#        #build and return list of stations and distances    
#        for record in listOfStations:
#            stationID = record[0]
#            stationDistance = record[-1].__float__()
#            listToReturn.append([stationID,stationDistance])
#        
#        return listToReturn    




class Tweet(object):
    '''
    usage:
    from db import dbfuncs
    '''
    def __init__(self):
        #establish db connection
        self.con = Connector()
        
      
    def loadTweet(self,tweetDict):
        #TODO: Update doc string
        '''
        pass in dictionary matching format produced TODO: WHERE by wxtalk.wxcollector.createMetarTable.getMetarDict(metarString)
        loads tweet
        if tweet exists already, then assume this is updated version --> delete existing, then create new record
        '''
        
        #throw error if data passed in is not a dict
        if type(tweetDict) != type({}):
            raise Exception("This function expects a dictionary containing metar data")

        #inspired by http://stackoverflow.com/questions/29461933/insert-python-dictionary-using-psycopg2
        #convert keys to column names and then create string
        columns = tweetDict.keys()
        columns_str = ", ".join(columns)
        #convert values to column names and then create string
        values = [tweetDict[x] for x in columns]
        values_str_list = [str(value) for value in values]
        #print values_str_list
        #print "helpo"
        #values_str_list = [str(value) for value in values]
        values_str = "\',\'".join(values_str_list).encode('utf-8').strip()
        #create insert string
#  orig-db ->>      sqlinsertstring = 'INSERT INTO weather.tweet (' + columns_str + ')\
#                                 VALUES (\'' + values_str + '\');'
        sqlinsertstring = 'INSERT INTO weather.tweets (' + columns_str + ')\
                                 VALUES (\'' + values_str + '\');'                                                   

        #load tweet into db
        #if exception thrown, then record likely exists, therefore delete record and try again
        try:
            self.con.cursor.execute(sqlinsertstring)
            self.con.connection.commit()
        except psycopg2.IntegrityError as error:
            try:
                #restablish connection, try to delete existing record and then insert in new record
                self.con.cursor.close()
                self.con = Connector()
# orig-db ->>               sqldeletestring = 'DELETE FROM weather.tweet\
#                            WHERE id = \'' + str(tweetDict['id']) + '\''
                sqldeletestring = 'DELETE FROM weather.tweets\
                            WHERE id = \'' + str(tweetDict['id']) + '\''
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
                    logger1.error('DB loadTweet: %s',  error)
                    #logger1.error('DB loadTweet'+ str(tweetDict['id']) +' : %s',  error.pgcode)
                raise Exception("Record could not be deleted nor inserted.  Review original tweet, most likely a report that is not in master station list")    

