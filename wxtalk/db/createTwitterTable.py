#Author: Steven Zimmerman
#Date: 20-JUN-2015

#Modified code from http://zetcode.com/db/postgresqlpythontutorial/


#TODO: change this to a less dangerous script, perhaps db build goes into one script

import psycopg2
import sys

#TODO: Add constraints for climate

def createTwitterTable():
    #open database connection
    connection = psycopg2.connect("dbname=weather user=steven password=steven") 
    cursor = connection.cursor()
    
#    #drop existing table
#    cursor.execute("DROP TABLE weather.tweets;")
#    connection.commit()
    
    
    #open database connection
    connection = psycopg2.connect("dbname=weather user=steven password=steven") 
    cursor = connection.cursor()

    #create table
    addTableCmd = "CREATE TABLE weather.tweets \
    (\
    id bigint PRIMARY KEY,\
    coordinates point,\
    created_at timestamp,\
    user_id bigint,\
    climate_uid integer,\
    climate_delta_time_sec float,\
    climate_station_dist float,\
    climate_station_id CHAR(4),\
    climate_secondary_uid integer,\
    climate_secondary_delta_time_sec float,\
    metar_uid integer,\
    metar_delta_time_sec float,\
    metar_station_dist float,\
    metar_station_id CHAR(4),\
    sentiment_class smallint,\
    sentiment_probability float,\
    weather_class boolean,\
    topic_obama boolean,\
    topic_adidas boolean,\
    topic_nike boolean,\
    topic_boeing boolean,\
    topic_microsoft boolean,\
    topic_tableau boolean,\
    topic_verizon boolean,\
    topic_apple boolean,\
    topic_samsung boolean,\
    topic_walmart boolean,\
    CONSTRAINT tweet_metar_station_icao_id_fkey FOREIGN KEY (metar_station_id)\
      REFERENCES weather.stations (icao_id) MATCH SIMPLE\
      ON UPDATE NO ACTION ON DELETE NO ACTION,\
    CONSTRAINT tweet_metar_report_uid_fkey FOREIGN KEY (metar_uid)\
      REFERENCES weather.metar (uid) MATCH SIMPLE\
      ON UPDATE NO ACTION ON DELETE NO ACTION);"
      
    cursor.execute(addTableCmd)
    connection.commit()






