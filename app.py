# Import the dependencies.
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, render_template, jsonify


#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

engine = create_engine('sqlite:///C:\\Users\\Saint\\Downloads\\mod10source\\Starter_Code\\Resources\\hawaii.sqlite')
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
session = Session()
# reflect the tables


# Save references to each table
tables = {table_name: getattr(Base.classes, table_name) for table_name in Base.classes.keys()}


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= start_date).all()
start_date = most_recent_date - timedelta(days=365)


#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    return (
        f"Welcome to the Climate API!<br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/&lt;start&gt;<br>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br>"
    )
@app.route('/api/v1.0/precipitation')
def precipitation():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')

results = session.query(Measurement.date, Measurement.prcp).filter(
    Measurement.date >= start_date,
    Measurement.prcp != None  
    ).all()
precipitation_data = {date: prcp for date, prcp in results}

@app.route('/data')
def data():
    result = session.query(tables['Measurement'].tobs).all()  # Adjust to your table
    data_list = [item[0] for item in result]
    return jsonify(data_list)
@app.route('/api/v1.0/tobs')
def tobs():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')

    start_date = most_recent_date - timedelta(days=365)
    most_active_station = session.query(
        Measurement.station, func.count(Measurement.station)
    ).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    
    results = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.station == most_active_station,
        Measurement.date >= start_date
    ).all()
    return jsonify(temperature_data)

@app.route('/api/v1.0/stations')
def stations():
    stations = session.query(Measurement.station).distinct().all()
    stations_list = [station[0] for station in stations]
    return jsonify(stations_list)

@app.route('/api/v1.0/<start>')
def start_date(start):
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        abort(400, description="Invalid date format. Please use YYYY-MM-DD format.")

@app.route('/api/v1.0/<start>/<end>')
def start_end_date(start, end):
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
    except ValueError:
        abort(400, description="Invalid date format. Please use YYYY-MM-DD format.")

    temperature_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    return jsonify(temperature_stats)



