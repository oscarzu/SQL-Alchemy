import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# engine = create_engine("sqlite:///Resources/hawaii.sqlite")
engine = create_engine('sqlite:///Resources/hawaii.sqlite', connect_args={'check_same_thread': False}, echo=True)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create session from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():

     return (
         f"Available Routes:<br/>"
         f"/api/v1.0/precipitation"
         f"- Dates and temperature observations from the last year<br/>"

         f"/api/v1.0/stations"
         f"- List of stations<br/>"

         f"/api/v1.0/tobs"
         f"- Temperature Observations from the past year<br/>"

         f"/api/v1.0/<start>"
         f"- Minimum temperature, the average temperature, and the max temperature for a given start day<br/>"

         f"/api/v1.0/<start>/<end>"
         f"- Minimum temperature, the average temperature, and the max temperature for a given range of days (start-end)<br/>"
     )


@app.route("/api/v1.0/precipitation")
def precip():
	"""Display a list of rain fall ordered in by descending date for clarity"""
	last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
	last_year = dt.date(2017, 8, 23) - dt.timedelta(days=366)
	rain_results = session.query(Measurement.date, Measurement.prcp).\
		filter(Measurement.date > last_year).order_by(Measurement.date).all()

	rain_season = []
	for date, prcp in rain_results:
		data = {}
		data['date'] = date
		data['prcp'] = prcp
		rain_season.append(data)

	return jsonify(rain_season)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    results = session.query(Station.name, Station.station, Station.elevation).all()

    #create dictionary for JSON
    station_list = []
    for result in results:
        row = {}
        row['name'] = result[0]
        row['station'] = result[1]
        row['elevation'] = result[2]
        station_list.append(row)
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def temp_obs():
    """Return a list of temperature observations for the previous year"""
    results = session.query(Station.name, Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= "2016-01-01", Measurement.date <= "2017-01-01").\
        all()

    #use dictionary, create json
    tobs_list = []
    for result in results:
        row = {}
        row["Date"] = result[1]
        row["Station"] = result[0]
        row["Temperature"] = int(result[2])
        tobs_list.append(row)

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start(start=None):
    # Docstring
    """Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""

    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),
                               func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(
        Measurement.date).all()
    from_start_list = list(from_start)
    return jsonify(from_start_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    # Docstring
    """Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""

    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),
                                  func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(
        Measurement.date <= end).group_by(Measurement.date).all()
    between_dates_list = list(between_dates)
    return jsonify(between_dates_list)



if __name__ == '__main__':
    app.run(debug=True)