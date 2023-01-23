import numpy as np
import datetime as dt
import pandas as pd

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
Base.prepare(autoload_with=engine)

# Set the start and end date for the precipitation data
start_date = dt.date(2016, 8, 23)
end_date = dt.date(2017, 8, 23)

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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Retrieve the last 12 months of precipitation data"""
    results = session.query(Measurement.date, 
                            Measurement.prcp).filter(Measurement.date >= start_date, 
                            Measurement.date <= end_date).all()
    
    session.close()

    # Create a dictionary from the row data to a list of precipitation data
    prcp_analysis = []
    for date, prcp in results:
        date_dict = {}
        date_dict["date"] = date
        date_dict["prcp"] = prcp
        prcp_analysis.append(date_dict)

    return jsonify(prcp_analysis)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    results = session.query(Measurement.station).group_by(Measurement.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature observations for the previous year"""
    results = session.query(Measurement.date, 
                            Measurement.tobs).filter(Measurement.date >= start_date, 
                            Measurement.date <= end_date,
                            Measurement.station == 'USC00519281').all()
    
    session.close()

    # Convert list of tuples into normal list
    all_temp = list(np.ravel(results))

    return jsonify(all_temp)


@app.route("/api/v1.0/<start_date>")
def temp_by_start_date(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Fetch the start date as a parameter and return the min, max and average
       temperatures calculated from the given start date to the end of the dataset""" 
    results = session.query(func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs)).\
                                filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    session.close()

    # Create a dictionary from the row data to a list of precipitation data
    temp_analysis = []
    for min, max, avg in results:
        temp_dict = {}
        temp_dict["Min"] = min
        temp_dict["Max"] = max
        temp_dict["Avg"] = avg
        temp_analysis.append(temp_dict)

    # If query result does not match parameters, return an error message
    if temp_dict["Min"]:
        return jsonify(temp_analysis)
    else:
        return jsonify({"error": f"Date {start_date} not found or not formatted as YYYY-MM-DD."}), 404


@app.route("/api/v1.0/<start_date>/<end_date>")
def temp_by_start_end_date(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Fetch the start and end date as a parameter and return the min, max and average
       temperatures calculated from the given start date to the given end date"""
    results = session.query(func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs)).\
                                filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    session.close()

    # Create a dictionary from the row data to a list of precipitation data
    temp_analysis = []
    for min, max, avg in results:
        temp_dict = {}
        temp_dict["Min"] = min
        temp_dict["Max"] = max
        temp_dict["Avg"] = avg
        temp_analysis.append(temp_dict)

    # If query result does not match parameters, return an error message
    if temp_dict["Min"]:
        return jsonify(temp_analysis)
    else:
        return jsonify({"error": f"Dates {start_date}/{end_date} not found, out of range or not formatted as YYYY-MM-DD."}), 404


if __name__ == "__main__":
    app.run(debug=True)