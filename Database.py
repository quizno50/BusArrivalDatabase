import sqlite3
import datetime
import logging

log = logging.getLogger("BusArrivalDatabase.Database")
logging.basicConfig(level=logging.INFO)

def getAllStops(dbCur):
	return dbCur.execute("SELECT * FROM stops;").fetchall()

def getAllRoutes(dbCur):
	return dbCur.execute("SELECT * FROM routes;").fetchall()

def insertArrival(db, stop, route, expectedArrival, actualArrival,
		commit=True):
	insertionQuery = "INSERT INTO arrival VALUES (?, ?, ?, ?);"
	values = (route, expectedArrival, actualArrival, stop)
	log.info("Inserting: {}".format(str(values)))
	db.execute(insertionQuery, values)
	if commit:
		db.commit()

def getDatabaseConnection():
	db = sqlite3.connect("late_busses.db")
	db.execute('CREATE TABLE IF NOT EXISTS stops (id INTEGER primary key, '
			'coords varchar(24), name varchar(64));')
	db.execute('CREATE TABLE IF NOT EXISTS arrival (route_id integer, '
			'scheduled_arrival datetime not null, '
			'actual_arrival datetime not null, stop integer);')
	db.execute('CREATE TABLE IF NOT EXISTS routes (id integer primary key, '
			'number integer, name varchar(64))')
	db.execute("CREATE TABLE IF NOT EXISTS schedule (stop_id INTEGER, "
			"route_id INTEGER, valid_from DATETIME, valid_to DATETIME, "
			"arrival_time TIME, foreign key(stop_id) references stops(id) "
			"on delete cascade on update cascade, "
			"foreign key (route_id) references routes(id) "
			"on delete cascade on update cascade)")
	return db

