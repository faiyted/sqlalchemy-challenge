# Import the dependencies.
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)



#################################################
# Flask Routes
#################################################
# Convert the query results from your precipitation analysis 
# (i.e. retrieve only the last 12 months of data) to a dictionary using 
# date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the SQL-Alchemy API!<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<startDate><br/>"
        f"/api/v1.0/<startDate>/<endDate><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Date 12 months ago


    # Perform a query to retrieve the data and precipitation scores
    result = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    # Convert the result to a list of dictionaries
    precipitation_data = []
    for date, prcp in result:
        prcp_data = {}
        prcp_data["date"] = date
        prcp_data["prcp"] = prcp
        precipitation_data.append(prcp_data)
    return jsonify(precipitation_data)

# Return a JSON list 
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

# Query the dates and temperature observations of the most-active

@app.route("/api/v1.0/tobs")
def temperature():
    session = Session(engine)
    results = session.query(Measurement.date,  Measurement.tobs,Measurement.prcp).\
                filter(Measurement.date >= '2016-08-23').\
                filter(Measurement.station=='USC00519281').\
                order_by(Measurement.date).all()
    session.close()
    tempData = []
    for result in results:
        tempDict = {result.date: result.tobs}

        tempData.append(tempDict)

    return jsonify(tempData)

# Return a JSON list of the min, avg, max temp for a specified start date
# Date must be keyed YYYY-MM-DD
@app.route('/api/v1.0/<startDate>')
def start(startDate):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= startDate).all()

    session.close()

    dates = []                       
    for  min, avg,max in results:
        date_dict = {}  
        date_dict["Min_Temp"] = min
        date_dict["Avg_Temp"] = avg
        date_dict["Max_Temp"] = max
        dates.append(date_dict)
    return jsonify(dates)

# Return a JSON list of the min, avg, max temp for a specified start-end range
# Date must be keyed YYYY-MM-DD/YYYY-MM-DD
@app.route('/api/v1.0/<startDate>/<endDate>')
def startEnd(startDate, endDate):
    
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= endDate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for date, min, avg,max in results:
        date_dict = {}
        date_dict["Date"] = date
        date_dict["Min_Temp"] = min
        date_dict["Avg_Temp"] = avg
        date_dict["Max_Temp"] = max
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)
