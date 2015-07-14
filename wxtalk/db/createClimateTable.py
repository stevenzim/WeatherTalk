#Author: Steven Zimmerman
#Date: 30-JUN-2015

#Modified code from http://zetcode.com/db/postgresqlpythontutorial/

##NOTE you must be logged in as postgres user & be in the directory where this script is stored
#user@ubuntu-dev:~/Desktop/GitHub/WeatherTalk/WeatherScripts$ sudo su - postgres
#postgres@ubuntu-dev:~$ cd /home/user/Desktop/GitHub/WeatherTalk/WeatherScripts

#TODO: change this to a less dangerous script, perhaps db build goes into one script

import psycopg2
import sys
from wxtalk.db import dbfuncs as db

def createClimateTable():
    #open database connection
    d = db.Connector()

    #drop existing table
    #d.cursor.execute("DROP TABLE weather.climate;")
    #d.connection.commit()


    addTableCmd = "CREATE TABLE weather.climate \
    (\
    icao_id CHAR(4),\
    report_date date,\
    precipitation_liquid_departure float,\
    precipitation_liquid_new_record smallint,\
    precipitation_liquid_observed float,\
    precipitation_snowfall_departure float,\
    precipitation_snowfall_new_record smallint,\
    precipitation_snowfall_observed float,\
    skies_average_sky_cover float,\
    total_sun_potential smallint,\
    temperature_maximum_departure float,\
    temperature_maximum_new_record smallint,\
    temperature_maximum_observed float,\
    temperature_minimum_departure float,\
    temperature_minimum_new_record smallint,\
    temperature_minimum_observed float,\
    winds_average_wind_speed float,\
    winds_highest_gust_speed float,\
    winds_highest_wind_speed float,\
    report_start_datetime timestamp,\
    report_end_datetime timestamp,\
        avg_two_day_precipitation_liquid_departure float,\
        avg_two_day_precipitation_liquid_observed float,\
        avg_two_day_precipitation_snowfall_departure float,\
        avg_two_day_precipitation_snowfall_observed float,\
        avg_two_day_temperature_maximum_departure float,\
        avg_two_day_temperature_maximum_observed float,\
        avg_two_day_temperature_minimum_departure float,\
        avg_two_day_temperature_minimum_observed float,\
        avg_two_day_winds_average_wind_speed float,\
        avg_two_day_skies_average_sky_cover float,\
    avg_three_day_precipitation_liquid_departure float,\
    avg_three_day_precipitation_liquid_observed float,\
    avg_three_day_precipitation_snowfall_departure float,\
    avg_three_day_precipitation_snowfall_observed float,\
    avg_three_day_temperature_maximum_departure float,\
    avg_three_day_temperature_maximum_observed float,\
    avg_three_day_temperature_minimum_departure float,\
    avg_three_day_temperature_minimum_observed float,\
    avg_three_day_winds_average_wind_speed float,\
    avg_three_day_skies_average_sky_cover float,\
        avg_seven_day_precipitation_liquid_departure float,\
        avg_seven_day_precipitation_liquid_observed float,\
        avg_seven_day_precipitation_snowfall_departure float,\
        avg_seven_day_precipitation_snowfall_observed float,\
        avg_seven_day_temperature_maximum_departure float,\
        avg_seven_day_temperature_maximum_observed float,\
        avg_seven_day_temperature_minimum_departure float,\
        avg_seven_day_temperature_minimum_observed float,\
        avg_seven_day_winds_average_wind_speed float,\
        avg_seven_day_skies_average_sky_cover float,\
    avg_thirty_day_precipitation_liquid_departure float,\
    avg_thirty_day_precipitation_liquid_observed float,\
    avg_thirty_day_precipitation_snowfall_departure float,\
    avg_thirty_day_precipitation_snowfall_observed float,\
    avg_thirty_day_temperature_maximum_departure float,\
    avg_thirty_day_temperature_maximum_observed float,\
    avg_thirty_day_temperature_minimum_departure float,\
    avg_thirty_day_temperature_minimum_observed float,\
    avg_thirty_day_winds_average_wind_speed float,\
    avg_thirty_day_skies_average_sky_cover float,\
    uid SERIAL UNIQUE,\
    PRIMARY KEY (ICAO_ID, report_date),\
    CONSTRAINT climate_report_station_id_fkey FOREIGN KEY (icao_id)\
      REFERENCES weather.stations (icao_id) MATCH SIMPLE\
      ON UPDATE NO ACTION ON DELETE NO ACTION\
    );"
    d.cursor.execute(addTableCmd)
    d.connection.commit()




#'CREATE INDEX climate_start_datetime_idx ON weather.climate (report_start_datetime);'





