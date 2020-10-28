import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Create session
#################################################
# session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

#Create Flask routes
@app.route("/")
def home():
    return (
        f'Home page'
        f'Available Routes:</br>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/<start></br>'
        f'/api/v1.0/<start>/<end></br>'
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session
    session = Session(engine)

    # Find the latest date in the dataset
    last_date_val = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date_val = dt.datetime.strptime(last_date_val, '%Y-%m-%d')

    # Get the date value from 1 year prior to the last date
    last_date_val = dt.date(last_date_val.year, last_date_val.month, last_date_val.day)
    pyear_date_val = dt.date(last_date_val.year -1, last_date_val.month, last_date_val.day)

    precip_data = session.query(Measurement.date, Measurement.prcp) \
                         .filter(Measurement.date>=pyear_date_val).all()

    # Convert to list of dictionaries to jsonify
    precip_data_list = []

    for date, precipitation in precip_data:
        precip_dict = {}
        precip_dict[date] = precipitation
        precip_data_list.append(precip_dict)

    session.close()
    return jsonify(precip_data_list)

@app.route("/api/v1.0/stations")
def stations():
    # Create session
    session = Session(engine)

    stations = {}

    # Query the list a stations
    query_results = session.query(Station.id, Station.station).all()
    for id, name in query_results:
        stations[id] = name

    session.close()

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def active_station_observations():

    #Create session
    session = Session(engine)

    # Find the latest date in the dataset
    last_date_val = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date_val = dt.datetime.strptime(last_date_val, '%Y-%m-%d')

    # Get the date value from 1 year prior to the last date
    last_date_val = dt.date(last_date_val.year, last_date_val.month, last_date_val.day)
    pyear_date_val = dt.date(last_date_val.year -1, last_date_val.month, last_date_val.day)

    max_observations = session.query(Measurement.date, Measurement.tobs) \
                                 .filter(Measurement.station == 'USC00519281') \
                                 .filter(Measurement.date > pyear_date_val).all()

    most_active_station = []

    for station, amt in max_observations:
        new_dict = {}
        new_dict[station] = amt
        most_active_station.append(new_dict)

    session.close()   

    return jsonify(most_active_station)

@app.route("/api/v1.0/<start>")
def start_data(start):

    session = Session(engine)

    value_list = []

    query_results = session.query( Measurement.date,\
                                  func.min(Measurement.tobs),\
                                  func.max(Measurement.tobs),\
                                  func.avg(Measurement.tobs)).\
                                  filter(Measurement.date >= start).all()
        
    
    for date, min, max, avg in query_results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TMAX"] = max
        new_dict["TAVG"] = avg
        value_list.append(new_dict)

    session.close()

    return jsonify(value_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end_data(start, end):

    session = Session(engine)

    value_list = []

    query_results = session.query( Measurement.date,\
                                  func.min(Measurement.tobs),\
                                  func.max(Measurement.tobs),\
                                  func.avg(Measurement.tobs)).\
                                  filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        
    
    for date, min, max, avg in query_results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TMAX"] = max
        new_dict["TAVG"] = avg
        value_list.append(new_dict)

    session.close()

    return jsonify(value_list)



if __name__ == '__main__':
    app.run(debug=True)