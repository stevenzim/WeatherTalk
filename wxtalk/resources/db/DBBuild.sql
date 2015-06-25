-- Database: weather

-- DROP DATABASE weather;

CREATE DATABASE weather
  WITH OWNER = postgres
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'en_GB.UTF-8'
       LC_CTYPE = 'en_GB.UTF-8'
       CONNECTION LIMIT = -1;

-- Extension: cube

-- DROP EXTENSION cube;

 CREATE EXTENSION cube
  SCHEMA public
  VERSION "1.0";
  
-- Extension: earthdistance

-- DROP EXTENSION earthdistance;

 CREATE EXTENSION earthdistance
  SCHEMA public
  VERSION "1.0";

-- Extension: plpgsql

-- DROP EXTENSION plpgsql;

 CREATE EXTENSION plpgsql
  SCHEMA pg_catalog
  VERSION "1.0";  
  
  
-- Schema: weather

-- DROP SCHEMA weather;

CREATE SCHEMA weather
  AUTHORIZATION postgres;

GRANT ALL ON SCHEMA weather TO postgres;
GRANT ALL ON SCHEMA weather TO steven;

-- Table: weather.climatestations

-- DROP TABLE weather.climatestations;

CREATE TABLE weather.climatestations
(
  icao_id character(4) NOT NULL,
  latitude double precision,
  longitude double precision,
  location point,
  name character varying(50),
  CONSTRAINT climatestations_pkey PRIMARY KEY (icao_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE weather.climatestations
  OWNER TO steven;

-- Table: weather.metarstations

-- DROP TABLE weather.metarstations;

CREATE TABLE weather.metarstations
(
  icao_id character(4) NOT NULL,
  latitude double precision,
  longitude double precision,
  location point,
  name character varying(50),
  CONSTRAINT metarstations_pkey PRIMARY KEY (icao_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE weather.metarstations
  OWNER TO steven;  
  
-- Table: weather.metar_report

-- DROP TABLE weather.metar_report;

CREATE TABLE weather.metar_report
(
  icao_id character(4) NOT NULL,
  observation_time timestamp without time zone NOT NULL,
  temp_c double precision,
  dewpoint_c double precision,
  wind_dir_degrees smallint,
  wind_speed_kt smallint,
  wind_gust_kt smallint,
  visibility_statute_mi double precision,
  altim_in_hg double precision,
  corrected boolean,
  maintenance_indicator_on boolean,
  wx_string character(20),
  precip_rain smallint,
  precip_snow smallint,
  precip_drizzle smallint,
  precip_unknown smallint,
  thunderstorm boolean,
  hail_graupel_pellets boolean,
  fog_mist boolean,
  transmissivity_clouds double precision,
  max_cloud_cov double precision,
  metar_type character(10),
  remark text,
  uid serial NOT NULL,
  CONSTRAINT metar_report_pkey PRIMARY KEY (icao_id, observation_time),
  CONSTRAINT metar_report_station_id_fkey FOREIGN KEY (icao_id)
      REFERENCES weather.metarstations (icao_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT metar_report_uid_key UNIQUE (uid)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE weather.metar_report
  OWNER TO steven;

-- Index: weather.observation_time_idx

-- DROP INDEX weather.observation_time_idx;

CREATE INDEX observation_time_idx
  ON weather.metar_report
  USING btree
  (observation_time);
  
  
-- Table: weather.tweet

-- DROP TABLE weather.tweet;

CREATE TABLE weather.tweet
(
  id bigint NOT NULL,
  coordinates point,
  created_at timestamp without time zone,
  text character varying(160),
  user_id bigint,
  user_name character varying(20),
  climate_db_uid integer,
  climate_delta_time_sec double precision,
  climate_station_dist double precision,
  climate_station_id character(4),
  metar_db_uid integer,
  metar_delta_time_sec double precision,
  metar_station_dist double precision,
  metar_station_id character(4),
  sentiment_score smallint,
  sentiment_positive boolean,
  sentiment_negative boolean,
  sentiment_neutral boolean,
  topic_weather boolean,
  topic_obama boolean,
  topic_microsoft boolean,
  topic_boeing boolean,
  topic_adidas boolean,
  CONSTRAINT tweet_pkey PRIMARY KEY (id),
  CONSTRAINT metar_station_id_fkey FOREIGN KEY (metar_station_id)
      REFERENCES weather.metarstations (icao_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT tweet_metar_report_id_fkey FOREIGN KEY (metar_db_uid)
      REFERENCES weather.metar_report (uid) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE weather.tweet
  OWNER TO steven;

