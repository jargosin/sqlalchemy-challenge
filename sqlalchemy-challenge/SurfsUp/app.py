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

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Set the start and end date for the precipitation data
start_date = dt.date(2016, 8, 23)
end_date = dt.date(2017, 8, 23)

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
        f"/api/v1.0/precipitation"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Retrieve the last 12 months of precipitation data"""
    # Query precipitation data
    yearly_prcp = session.query(Measurement.date, 
                                Measurement.prcp).filter(Measurement.date >= start_date, 
                                                     Measurement.date <= end_date).all()
    
    session.close()

    # Convert list of tuples into normal list
    prcp_analysis = list(np.ravel(yearly_prcp))

    return jsonify(prcp_analysis)


if __name__ == "__main__":
    app.run(debug=True)