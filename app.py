# Import dependencies 

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
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for dates and precipitation values
    results = session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date).all()

    date_prcp_list = []

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    for date, prcp in results:
        date_prcp_dict = {}
        date_prcp_dict[date] = prcp
        date_prcp_list.append(date_prcp_dict)

    return jsonify(date_prcp_list)
    session.close()

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query for the Station ID and names for all stations
    results = session.query(Station.station, Station.name).all()

    station_list = [] 
    for station, name in results:
        station_dict = {}
        station_dict[station] = name
        station_list.append(station_dict)

    session.close()
    return jsonify(station_list) 

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Retrieve the last date in the database 
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = most_recent_date[0]

    # Convert the date into a datetime object 
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")

    # Get last year's date 
    query_date = most_recent_date-dt.timedelta(days = 365)

    # Retrieve name and temperature counts for the most active station 
    temp_obs = session.query(Measurement.station, func.count(Measurement.tobs)).\
        group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc()).all()
    station_highest = temp_obs[0][0]

    # Query for the temperature observations for the last year of data
    last_12 = session.query(Measurement.tobs).\
        filter(Measurement.station == station_highest).\
        filter(Measurement.date >= query_date).all()

    # Get a list of a 1-D array of the query
    normal_list = list(np.ravel(last_12))
    session.close()
    return jsonify(normal_list)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start = None, end = None):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Get the minimum temperature, average temperature, and max temperature 
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
    if not end:
        temps = session.query(*sel).filter(Measurement.date >= start).all()
        temps_list = list(np.ravel(temps))
        return jsonify(temps_list)
    
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive
    new_temps = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    return jsonify(new_temps)

    session.close()

if __name__ == '__main__':
    app.run(debug=True)  
     