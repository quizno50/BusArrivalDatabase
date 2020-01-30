#!/usr/bin/env python3
import datetime
import sys
import logging
import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import Parser
import Database
import DateTimeTools

class DatabaseListWidget(QtWidgets.QListWidget):
	def __init__(self, parent, dbCxn, dbTableName, displayColumn=1,
			itemIcon=None):
		super(DatabaseListWidget, self).__init__(parent)
		self._dbCxn = dbCxn
		self._tableName = dbTableName
		self._displayColumn = displayColumn
		self._itemIcon = itemIcon
		self.refreshListItems()
	
	def refreshListItems(self):
		cur = self._dbCxn.cursor()
		res = cur.execute("SELECT * FROM {}".format(self._tableName))
		while self.count() > 0:
			self.removeItemWidget(self.row(0))
		for item in res:
			listItem = QtWidgets.QListWidgetItem(str(item[self._displayColumn]))
			if self._itemIcon is not None:
				listItem.setIcon(QtGui.QIcon(self._itemIcon))
			listItem.setData(1337, item[0])
			log.debug("Setting item data(1337) to {}".format(item[0]))
			self.addItem(listItem)

class StopsListWidget(DatabaseListWidget):
	def __init__(self, parent, dbCxn):
		super(StopsListWidget, self).__init__(parent, dbCxn, "stops", 2,
				"octagonal-sign_1f6d1.png")
		self.currentRowChanged.connect(self.doChange)

	def setArrivalsList(self, arrivalsList):
		self.arrivalsList = arrivalsList

	def setRoutesList(self, routesList):
		self.routesList = routesList

	def doChange(self, row):
		item = self.item(row)
		if self.routesList.currentItem() is not None:
			self.arrivalsList.refreshListItems(self.routesList.currentItem().data(
					1337), item.data(1337))
				

class RoutesListWidget(DatabaseListWidget):
	def __init__(self, parent, dbCxn):
		super(RoutesListWidget, self).__init__(parent, dbCxn, "routes", 1,
				"bus_1f68c.png")
		self.currentRowChanged.connect(self.doChange)

	def setArrivalsList(self, arrivalsList):
		self.arrivalsList = arrivalsList

	def setStopsList(self, stopsList):
		self.stopsList = stopsList
	
	def doChange(self, row):
		item = self.item(row)
		if self.stopsList.currentItem() is not None:
			self.arrivalsList.refreshListItems(item.data(1337),
					self.stopsList.currentItem().data(1337))

# This isn't a DatabaseListWidget yet, not until we populate arrival times for
# different routes in the database. For now they are hard coded.
class ArrivalsListWidget(QtWidgets.QListWidget):
	def __init__(self, *args, **kwargs):
		self.dbCxn = kwargs["dbCxn"]
		del kwargs["dbCxn"]
		super(ArrivalsListWidget, self).__init__(*args, **kwargs)

	def refreshListItems(self, route, stop):
		cur = self.dbCxn.cursor()
		res = cur.execute("SELECT * FROM schedule WHERE stop_id = ? "
				"AND route_id = ? AND valid_from <= datetime() AND "
				"valid_to >= datetime();",
				(stop, route))
		while self.count() > 0:
			self.takeItem(0)
		for row in res.fetchall():
			listItem = QtWidgets.QListWidgetItem(str(row[4]))
			listItem.setIcon(QtGui.QIcon("alarm-clock_23f0.png"))
			self.addItem(listItem)

class QtArrivalInserter(QtWidgets.QMainWindow):
	def __init__(self):
		self.dbCxn = Database.getDatabaseConnection()
		super(QtArrivalInserter, self).__init__()
		self.setMinimumSize(700, 400)
		self.setWindowTitle("Bus Arrival Database Inserter")
		self.setCentralWidget(QtWidgets.QWidget(self))
		self.layout = QtWidgets.QGridLayout(self.centralWidget())
		self.centralWidget().setLayout(self.layout)
		self.layout.addWidget(QtWidgets.QLabel("Stop"), 0, 0, 1, 2)
		self.layout.addWidget(QtWidgets.QLabel("Route"), 0, 2)
		self.layout.addWidget(QtWidgets.QLabel("Expected Arrival"), 0, 3)
		self.stopsList = StopsListWidget(self.centralWidget(), self.dbCxn)
		self.layout.addWidget(self.stopsList, 1, 0, 1, 2)
		self.routesList = RoutesListWidget(self.centralWidget(), self.dbCxn)
		self.layout.addWidget(self.routesList, 1, 2)
		self.arrivalsList = ArrivalsListWidget(self.centralWidget(),
				dbCxn=self.dbCxn)
		self.layout.addWidget(self.arrivalsList, 1, 3)
		self.stopsList.setArrivalsList(self.arrivalsList)
		self.routesList.setArrivalsList(self.arrivalsList)
		self.stopsList.setRoutesList(self.routesList)
		self.routesList.setStopsList(self.stopsList)

		self.layout.addWidget(QtWidgets.QLabel("Current Time:"), 2, 0)
		self.currentTimeLabel = QtWidgets.QLabel("XX:XX:XX") 
		self.layout.addWidget(self.currentTimeLabel, 2, 1)

		self.currentTimeButton = QtWidgets.QPushButton("Insert Current Time")
		self.currentTimeButton.clicked.connect(self.insertCurrentTime)
		self.layout.addWidget(self.currentTimeButton , 2, 2)
		self.newTimeButton = QtWidgets.QPushButton("Insert Other Time")
		self.newTimeButton.clicked.connect(self.insertNewTime)

		self.layout.addWidget(self.newTimeButton , 2, 3)
		self.layout.setColumnStretch(0, 3)
		self.layout.setColumnStretch(1, 1)
		self.layout.setColumnStretch(2, 1)

		self.currentTimeTimer = QtCore.QTimer(self)
		self.currentTimeTimer.timeout.connect(self.updateCurrentTime)
		self.currentTimeTimer.start(1000)
	
	def updateCurrentTime(self):
		self.currentTimeLabel.setText(datetime.datetime.now().strftime(
				"%H:%M:%S"))

	def insertCurrentTime(self):
		Database.insertArrival(self.dbCxn,
				self.stopsList.currentItem().data(1337),
				self.routesList.currentItem().data(1337),
				DateTimeTools.dateAndTimeToDatetime(datetime.date.today(),
						Parser.parseTime(self.arrivalsList.currentItem().data(0))),
						datetime.datetime.now())

	def insertNewTime(self):
		newTime, status = QtWidgets.QInputDialog().getText(self,
				"Enter the arrival time", "Arrival Time",
				QtWidgets.QLineEdit.Normal, str(datetime.datetime.now()))
		if status:
			Database.insertArrival(self.dbCxn,
					self.stopsList.currentItem().data(1337),
					self.routesList.currentItem().data(1337),
					DateTimeTools.dateAndTimeToDatetime(datetime.date.today(),
							Parser.parseTime(self.arrivalsList.currentItem().data(0))),
					datetime.datetime.strptime(newTime, "%Y-%m-%d %H:%M:%S.%f"))

def main():
	app = QtWidgets.QApplication(sys.argv)
	gui = QtArrivalInserter()
	gui.show()
	sys.exit(app.exec_())

if __name__=='__main__':
	main()
