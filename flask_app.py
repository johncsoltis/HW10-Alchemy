from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
import datetime as dt
from sqlalchemy.orm import scoped_session, sessionmaker

###########################################
# Database Setup #
###########################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
data = engine.execute('select * from Measurement')
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = scoped_session(sessionmaker(bind=engine))

last_precip = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
last_precip = dt.datetime.strptime('2017-08-23', "%Y-%m-%d")
lastyear = last_precip - dt.timedelta(days=365)

##############################################
# Flask Routes #
##############################################

app = Flask(__name__)

@app.route("/")
def welcome():

    return(
        f"List of All Available API Routes:<br/>"
        f"The all dates and rainfall observations from last year:<br>"
        f"/precipitation<br/>"
        f"List of all stations from the dataset:<br>"
        f"/stations<br/>"
        f"List all of Temperature Observations (tobs) for the previous year:<br>"
        f"/tobs<br/>"
        f"List of the maximum temperature, the minumim temperature, and the average temperature for a given start date:<br>"
        f"/*start date in YYYY-MM-DD form*<br/>"
        f"List of the minimum temperature, the average temperature, and the max temperature for given start and end dates:<br>"
        f"/*start date in YYYY-MM-DD form*/*end date in YYYY-MM-DD form*<br/>"
    )

@app.route("/precipitation")
def precipitation():

    prcpdata = session.query(Measurement.date, Measurement.prcp).\
       filter(Measurement.date >= lastyear).\
       order_by(Measurement.date).all()
    
    precipitation_data = dict(prcpdata)
        
    return jsonify({'Data':precipitation_data})


@app.route("/stations")
def stations():

    stations = session.query(Station).all()
    stations_list = list()
    for station in stations:
        stations_dict = dict()
        stations_dict['Station'] = station.station
        stations_dict["Station Name"] = station.name
        stations_dict["Latitude"] = station.latitude
        stations_dict["Longitude"] = station.longitude
        stations_dict["Elevation"] = station.elevation
        stations_list.append(stations_dict)
    return jsonify ({'Data':stations_list})

@app.route("/tobs")
def tobs():

    tempdata = session.query(Measurement.tobs, Measurement.date, Measurement.station).\
    filter(Measurement.date >= lastyear).all()

    temp_list = list()
    for data in tempdata:
        temp_dict = dict()
        temp_dict['Station'] = data.station
        temp_dict['Date'] = data.date
        temp_dict['Temp'] = data.tobs
        temp_list.append(temp_dict)
        
    return jsonify ({'Data':temp_list})

@app.route("/<start>")
def start_temp(start=None):

        temps = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(
    	Measurement.date >= start
    ).\
    group_by(Measurement.date).all()


@app.route("/<start>/<end>")
def calc_temps(start=None,end=None):
    temps = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(
    	Measurement.date >= start,
    	Measurement.date <= end
    ).\
    group_by(Measurement.date).all()



    return jsonify (temps)
 

if __name__ == '__main__':
    app.run(debug=True, port=5001)