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

    prcp_list = []

    for date, prcp in results:
        empty_dict = {}
        empty_dict[date] = prcp
        prcp_list.append(empty_dict)

    session.close()

    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(Station.station, Station.name).all()

    station_list = [] 
    for station, name in results:
        empty_dict = {}
        empty_dict[station] = name
        station_list.append({name: station})
        #station_list.append(empty_dict)
    session.close()

    return jsonify(station_list) 

@app.route("/api/v1.0/tobs")
def tobs():
    print("here")
    session = Session(engine)
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = most_recent_date[0]
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    print(most_recent_date)
    query_date = most_recent_date-dt.timedelta(days = 365)
    temp_obs = session.query(Measurement.station, func.count(Measurement.tobs)).\
        group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc()).all()
    temp_highest = temp_obs[0][0]
    last_12 = session.query(Measurement.tobs).\
        filter(Measurement.station == temp_highest).\
        filter(Measurement.date >= query_date).all()
    normal_list = list(np.ravel(last_12))
    session.close()
    return jsonify(normal_list)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start = None, end = None):
    session = Session(engine)

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        temps = session.query(*sel).filter(Measurement.date >= start).all()
        temps_list = list(np.ravel(temps))
        print(temps_list)
        return jsonify(temps_list)
        
    new_temps = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    print(new_temps)        
    
    return jsonify(new_temps)
    session.close()

if __name__ == '__main__':
    app.run(debug=True)  
     