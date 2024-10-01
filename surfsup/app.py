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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
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
    return all_temps

if __name__ == "__main__":
    app.run(debug=True)

