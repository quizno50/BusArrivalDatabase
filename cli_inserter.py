#!/usr/bin/python3
import Database
import Parser
import DateTimeTools
import sqlite3
import sys
import datetime

def stopSelection(db):
	for stop in Database.getAllStops(db):
		print("   {:>3d}. {}".format(stop[0], stop[2]))
	print("Enter a stop number:")
	return int(sys.stdin.readline())

def getRoute(db):
	for route in Database.getAllRoutes(db):
		print("   {:>3d}. {} - ()".format(route[0], route[1], route[2]))
	print("Enter a route id:")
	return int(sys.stdin.readline())

def getDay():
	print("Enter a date (YYYY-MM-DD):")
	return Parser.parseDate(sys.stdin.readline())

def getTime(prompt=None):
	if prompt is not None:
		print("Enter a time for {}".format(prompt))
	else:
		print("Enter a time:")
	return Parser.parseTime(sys.stdin.readline())

def main():
	db = sqlite3.connect("late_busses.db")
	stop = stopSelection(db)
	route = getRoute(db)
	if "NotToday" in sys.argv:
		day = getDay()
	else:
		day = datetime.date.today()
	if "NotNow" in sys.argv:
		actualArrival = DateTimeTools.dateAndTimeToDatetime(day, getTime("Actual Arrival"))
	else:
		actualArrival = datetime.datetime.now()
	expectedArrival = DateTimeTools.dateAndTimeToDatetime(day, getTime("Expected Arrival"))
	Database.insertArrival(db, stop, route, expectedArrival, actualArrival)

if __name__=="__main__":
	main()

