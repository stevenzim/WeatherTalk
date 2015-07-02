#Author: Steven Zimmerman
#Date: 16-JUN-2015

#Modified code from http://zetcode.com/db/postgresqlpythontutorial/

##NOTE you must be logged in as postgres user & be in the directory where this script is stored
#user@ubuntu-dev:~/Desktop/GitHub/WeatherTalk/WeatherScripts$ sudo su - postgres
#postgres@ubuntu-dev:~$ cd /home/user/Desktop/GitHub/WeatherTalk/WeatherScripts

#TODO: change this to a less dangerous script, perhaps db build goes into one script

import psycopg2
import sys
from wxtalk.db import dbfuncs as db

def createMetarTable():
    #open database connection
    d = db.Connector()

    #drop existing table
#    d.cursor.execute("DROP TABLE weather.metar;")
#    d.connection.commit()

    #create table
    addTableCmd = "CREATE TABLE weather.metar \
    (\
    icao_id CHAR(4),\
    observation_time timestamp,\
    temp_c float,\
    dewpoint_c float,\
    wind_dir_degrees smallint,\
    wind_speed_kt smallint,\
    wind_gust_kt smallint,\
    visibility_statute_mi float,\
    altim_in_hg float,\
    corrected bool,\
    maintenance_indicator_on bool,\
    wx_string char(20),\
    precip_rain smallint,\
    precip_snow smallint,\
    precip_drizzle smallint,\
    precip_unknown smallint,\
    precip_intensity smallint,\
    precip_occuring bool,\
    thunderstorm bool,\
    hail_graupel_pellets bool,\
    fog_mist bool,\
    tornado bool,\
    three_hour_pressure_tendency float,\
    one_hour_precip float,\
    transmissivity_clouds float,\
    max_cloud_cov float,\
    metar_type char(10),\
    remark text,\
    uid SERIAL UNIQUE,\
    PRIMARY KEY (ICAO_ID, observation_time),\
    CONSTRAINT metar_report_station_id_fkey FOREIGN KEY (icao_id)\
      REFERENCES weather.stations (icao_id) MATCH SIMPLE\
      ON UPDATE NO ACTION ON DELETE NO ACTION\
    );"

    d.cursor.execute(addTableCmd)
    d.connection.commit()



#TODO: Uncomment this to run
#def createMetarTable():
#    #open database connection
#    connection = psycopg2.connect("dbname=weather user=steven password=steven") 
#    cursor = connection.cursor()

#    #drop existing table
#    cursor.execute("DROP TABLE weather.metar_report;")
#    connection.commit()


#    #open database connection
#    connection = psycopg2.connect("dbname=weather user=steven password=steven") 
#    cursor = connection.cursor()

#    #create table
#    addTableCmd = "CREATE TABLE weather.metar_report \
#    (\
#    ICAO_ID CHAR(4),\
#    observation_time timestamp,\
#    temp_c float,\
#    dewpoint_c float,\
#    wind_dir_degrees smallint,\
#    wind_speed_kt smallint,\
#    wind_gust_kt smallint,\
#    visibility_statute_mi float,\
#    altim_in_hg float,\
#    corrected bool,\
#    maintenance_indicator_on bool,\
#    wx_string char(20),\
#    precip_rain smallint,\
#    precip_snow smallint,\
#    precip_drizzle smallint,\
#    precip_unknown smallint,\
#    thunderstorm bool,\
#    hail_graupel_pellets bool,\
#    fog_mist bool,\
#    transmissivity_clouds float,\
#    max_cloud_cov float,\
#    metar_type char(10),\
#    remark text,\
#    uid SERIAL UNIQUE,\
#    PRIMARY KEY (ICAO_ID, observation_time),\
#    CONSTRAINT metar_report_station_id_fkey FOREIGN KEY (ICAO_ID)\
#      REFERENCES weather.metarStations (ICAO_ID) MATCH SIMPLE\
#      ON UPDATE NO ACTION ON DELETE NO ACTION\
#    );"

#    cursor.execute(addTableCmd)
#    connection.commit()

#'ALTER TABLE weather.metar_report ADD UNIQUE (uid);'
#'CREATE INDEX observation_time_idx ON weather.metar_report (observation_time);'
#'CREATE INDEX stationid_idx ON weather.metar_report (ICAO_ID);'

#'DROP INDEX weather.observation_time_idx;'

#determine size of table
#sql = 'SELECT reltuples::bigint AS estimate \
#FROM   pg_class \
#WHERE  oid = \'weather.metar_report\'::regclass;'

#get list of indexs
#sql = 'SELECT i.relname as indname,\
#       i.relowner as indowner,\
#       idx.indrelid::regclass,\
#       am.amname as indam,\
#       idx.indkey,\
#       ARRAY(\
#       SELECT pg_get_indexdef(idx.indexrelid, k + 1, true)\
#       FROM generate_subscripts(idx.indkey, 1) as k\
#       ORDER BY k\
#       ) as indkey_names,\
#       idx.indexprs IS NOT NULL as indexprs,\
#       idx.indpred IS NOT NULL as indpred \
#FROM   pg_index as idx \
#JOIN   pg_class as i \
#ON     i.oid = idx.indexrelid \
#JOIN   pg_am as am \
#ON     i.relam = am.oid;'
#c.cursor.execute(sql)
#t = c.cursor.fetchall()
#b = [(i[0]) for i in t]


#sudo service postgresql restart







