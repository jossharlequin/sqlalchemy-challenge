# Import the dependencies.



#################################################
# Database Setup
#################################################


# reflect an existing database into a new model

# reflect the tables


# Save references to each table


# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################

#################################################
# Flask Routes
#################################################


# Import necessary libraries
import datetime as dt
import numpy as np
import pandas as pd
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

# Create a Flask app
app = Flask(__name__)

# Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Reference the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

# Define the routes
@app.route("/")
def home():
    """Homepage."""
    return (
        f"Welcome to the Climate App API!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date (replace 'start_date' with a date in 'YYYY-MM-DD' format)<br/>"
        f"/api/v1.0/start_date/end_date (replace 'start_date' and 'end_date' with dates in 'YYYY-MM-DD' format)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data."""
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)
    precipitation_data = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= one_year_ago.strftime('%Y-%m-%d')).all()
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    stations_list = session.query(Station.station).all()
    return jsonify({"Stations": [station[0] for station in stations_list]})

@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations for the most active station in the last 12 months."""
    most_active_station_id = 'USC00519281'
    most_active_tobs_data = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station_id)\
        .filter(Measurement.date >= one_year_ago.strftime('%Y-%m-%d')).all()
    return jsonify({"Temperature Observations": most_active_tobs_data})

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return TMIN, TAVG, and TMAX for all dates greater than or equal to the start date."""
    temperature_stats = session.query(
        func.min(Measurement.tobs).label('TMIN'),
        func.avg(Measurement.tobs).label('TAVG'),
        func.max(Measurement.tobs).label('TMAX')
    ).filter(Measurement.date >= start).all()
    return jsonify(temperature_stats)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return TMIN, TAVG, and TMAX for dates from the start date to the end date, inclusive."""
    temperature_stats = session.query(
        func.min(Measurement.tobs).label('TMIN'),
        func.avg(Measurement.tobs).label('TAVG'),
        func.max(Measurement.tobs).label('TMAX')
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    return jsonify(temperature_stats)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)