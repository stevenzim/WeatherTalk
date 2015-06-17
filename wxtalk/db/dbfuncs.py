#author: Steven Zimmerman
#created: 09-JUN-2015
#module to retrieve wx station information from weather db

import psycopg2
import sys


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
        
    def loadMetarReport(self,metarDict):
        '''
        pass in dictionary matching format produced by wxtalk.wxcollector.createMetarTable.getMetarDict(metarString)
        loads metar report if it exists
        if it exists already, then assume this is updated version --> delete existing, then create new record
        '''
        
        ###Example to load in data into db
#        from wxtalk.wxcollector import processmetar as metar

#        metarRep1 = 'KNCA,2015-05-22T14:05:00Z,17.2,11.1,360,9,,10.0,30.15059,,,,BKN,3000,,,,,,,SPECI, AO2 T01720111'
#        metarList1 = metarRep1.split(",")
#        metarDict1 = metar.getMetarDict(metarList1)


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
            except:
                # if it can't be deleted or inserted, do warn me so I can review the data
                raise Exception("Record could not be deleted nor inserted.  Review original metar data")       

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



