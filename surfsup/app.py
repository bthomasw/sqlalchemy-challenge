import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_

from flask import Flask, jsonify

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


# 3. Define what to do when a user hits the index route
@app.route("/")
def home():
    return (
        f"Welcome to weather and temperature API<br/>"
        f"Available Routes<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-08-23 (calculates max, min, and avg temp after a certain date)<br/>"
        f"/api/v1.0/2016-08-23/2017-08-23 (calculates max, min, and avg temp between two dates)<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date_datetime = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    twelve_months_ago = most_recent_date_datetime - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > twelve_months_ago).all()

    session.close()

    precipitation_values = {}
    for date, prcp in results:
        precipitation_values[date] = prcp
    
    return jsonify(precipitation_values)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station)
    session.close()
    list_stations = []
    for station in results:
        next_station = str(station)
        list_stations.append(next_station)
    

    return jsonify(list_stations)

@app.route("/api/v1.0/tobs")
def temp_most_active_station():
    session = Session(engine)
    list_of_active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    most_active_station = list_of_active_stations[0][0]
    most_recent_date = session.query(func.max(Measurement.date)).scalar()

    session.close()
    most_recent_date_datetime = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    twelve_months_ago = most_recent_date_datetime - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(
            and_(
                Measurement.date > twelve_months_ago, Measurement.station == most_active_station
            )
        ).all()
    
    all_temps = list(np.ravel(results))
    return jsonify(all_temps)

@app.route("/api/v1.0/<start>")
def state_date(start):
    start_datetime = dt.datetime.strptime(start, '%Y-%m-%d')
    session = Session(engine)
    min_avg_max = session.query(func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date > start_datetime).all()
    session.close()
    return(f"Max Temp: {min_avg_max[0][0]}<br/>Min Temp: {min_avg_max[0][1]}<br/>Avg Temp: {min_avg_max[0][2]}")


@app.route("/api/v1.0/<start>/<end>")
def end_date(start, end):
    start_datetime = dt.datetime.strptime(start, '%Y-%m-%d')
    end_datetime = dt.datetime.strptime(end, '%Y-%m-%d')
    session = Session(engine)
    min_avg_max = session.query(func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(
            and_(
                Measurement.date > start_datetime, Measurement.date < end_datetime
            )
        ).all()
    session.close()
    return(f"Max Temp: {min_avg_max[0][0]}<br/>Min Temp: {min_avg_max[0][1]}<br/>Avg Temp: {min_avg_max[0][2]}")

if __name__ == "__main__":
    app.run(debug=True)

