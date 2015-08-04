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






#FK constrains on climate reports
#    CONSTRAINT tweet_climate_station_icao_id_fkey FOREIGN KEY (climate_station_id)\
#      REFERENCES weather.stations (icao_id) MATCH SIMPLE\
#      ON UPDATE NO ACTION ON DELETE NO ACTION,\
#    CONSTRAINT tweet_climate_report_uid_fkey FOREIGN KEY (climate_uid)\
#      REFERENCES weather.climate (uid) MATCH SIMPLE\
#      ON UPDATE NO ACTION ON DELETE NO ACTION)

#'CREATE INDEX tweet_metar_report_uid_idx ON weather.tweet (metar_db_uid);'
#'CREATE INDEX tweet_creation_idx ON weather.tweet (created_at);'

#'DROP INDEX weather.tweet_metar_report_uid_idx;'
#'DROP INDEX weather.tweet_creation_idx;'


#def createTwitterTable():
#    #open database connection
#    connection = psycopg2.connect("dbname=weather user=steven password=steven") 
#    cursor = connection.cursor()

    #drop existing table
#    cursor.execute("DROP TABLE weather.tweet;")
#    connection.commit()


#        #open database connection
#    connection = psycopg2.connect("dbname=weather user=steven password=steven") 
#    cursor = connection.cursor()

#    #create table
#    addTableCmd = "CREATE TABLE weather.tweet \
#    (\
#    id bigint PRIMARY KEY,\
#    coordinates point,\
#    created_at timestamp,\
#    text varchar(160),\
#    user_id bigint,\
#    user_name varchar(20),\
#    climate_db_uid integer,\
#    climate_delta_time_sec float,\
#    climate_station_dist float,\
#    climate_station_id CHAR(4),\
#    metar_db_uid integer,\
#    metar_delta_time_sec float,\
#    metar_station_dist float,\
#    metar_station_id CHAR(4),\
#    sentiment_score smallint,\
#    sentiment_positive boolean,\
#    sentiment_negative boolean,\
#    sentiment_neutral boolean,\
#    topic_weather boolean,\
#    topic_obama boolean,\
#    topic_microsoft boolean,\
#    topic_boeing boolean,\
#    topic_adidas boolean,\
#    CONSTRAINT metar_station_id_fkey FOREIGN KEY (metar_station_id)\
#      REFERENCES weather.metarStations (ICAO_ID) MATCH SIMPLE\
#      ON UPDATE NO ACTION ON DELETE NO ACTION,\
#    CONSTRAINT tweet_metar_report_id_fkey FOREIGN KEY (metar_db_uid)\
#      REFERENCES weather.metar_report (uid) MATCH SIMPLE\
#      ON UPDATE NO ACTION ON DELETE NO ACTION);"

#    cursor.execute(addTableCmd)
#    connection.commit()


#'CREATE INDEX tweet_metar_report_uid_idx ON weather.tweet (metar_db_uid);'
#'CREATE INDEX tweet_creation_idx ON weather.tweet (created_at);'

#'DROP INDEX weather.tweet_metar_report_uid_idx;'
#'DROP INDEX weather.tweet_creation_idx;'








