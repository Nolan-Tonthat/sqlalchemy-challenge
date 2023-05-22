# Import the dependencies.
from flask import Flask, jsonify

import numpy as np
import pandas as pd
from datetime import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.sql import exists  

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################


app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
#1. Start at the homepage and list all the available routes.
def welcome():
    """Here are the available routes: <br/>"""
    """NOTE: when entering start and end times, please enter in YYYY-MM-DD format"""
    return(  
        f"Available Routes:<br/>"
         f"/api/v1.0/precipitation<br/>"
         f"/api/v1.0/stations<br/>"
         f"/api/v1.0/tobs<br/>"
         f"/api/v1.0/<start><br/>"
         f"/api/v1.0/<start><end>"

    )


@app.route("/api/v1.0/precipitation")
#2a. Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
#2b. Return the JSON representation of your dictionary.
def precipitation():

    res = session.query(measurement.prcp, measurement.date).filter(measurement.date >= '2016-08-23').order_by(measurement.date).all()
    precip_dict = {date : row for date , row in res}
    return jsonify(precip_dict)


@app.route("/api/v1.0/stations")
#3. Return a JSON list of stations from the dataset.
def station():
    res = session.query(station.station).all()
    all_stations = list(np.ravel(res))
    return jsonify (all_stations)

@app.route("/api/v1.0/tobs")
#4a. Query the dates and temperature observations of the most-active station for the previous year of data.
#4b. Return a JSON list of temperature observations for the previous year.

def tobs():

    most_recent_datetime = dt.date(2017,8,23)

    one_year = dt.date(2016,8,23)

    year_tobs=(session.query(measurement.date,measurement.tobs).filter(func.strftime('%Y-%m-%d',measurement.date) >= one_year).group_by(measurement.date).all())
    tobs_list = list(np.ravel(year_tobs))
    return jsonify (tobs_list)


@app.route ("/api/v1.0/<start>")
#5a.Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#5b. For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
def temps1(start):
   
    start = dt.strptime(start,'%Y-%m-%d')
    temps = session.query(measurement.tobs).filter(measurement.date >= start)
    temps_list =[] 
    for row in temps:
        temps_list.append(row.tobs) 
    return (jsonify ({"tempmin": min(temps_list),"tempmax": max(temps_list),"tempavg":np.mean(temps_list)}))


@app.route ("/api/v1.0/<start>/<end>")
#5c.For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
def temps2(start,end):
   
    start = dt.strptime(start,'%Y-%m-%d')
    end = dt.strptime(end,'%Y-%m-%d')
    temps = session.query(measurement.tobs).filter(measurement.date >= start).filter(measurement.date <= end)
    temps_list =[] 
    for row in temps:
        temps_list.append(row.tobs) 
    return (jsonify ({"tempmin": min(temps_list),"tempmax": max(temps_list),"tempavg":np.mean(temps_list)}))
           

if __name__ == "__main__":
   app.run(debug=True)