import re
import datetime

DATE_REGEX = re.compile(r'(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-'
		'(?P<day>[0-9]{2})')

def parseDate(date):
	match = re.match(DATE_REGEX, date)
	return datetime.date(int(match.group("year")), int(match.group("month")),
			int(match.group("day")))

TIME_REGEX = re.compile(r'(?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):'
			'(?P<second>[0-9]{2})')

def parseTime(time):
	match = re.match(TIME_REGEX, time)
	return datetime.time(int(match.group("hour")), int(match.group("minute")),
			int(match.group("second")))

