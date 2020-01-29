import datetime

def dateAndTimeToDatetime(date, time):
	return datetime.datetime(date.year, date.month, date.day, time.hour,
			time.minute, time.second, 0)

