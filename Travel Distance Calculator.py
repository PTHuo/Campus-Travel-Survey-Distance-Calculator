#!/usr/bin/env python3
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QMessageBox

import pandas as pd
import numpy as np
import requests, os, math

origin = '38.53908008258149,-121.7520339149894' # The default orign point for the CTS is the intersection of California Ave and Hutchison Dr
max_dest = 25     # Google's limit of addresses
API_link = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial'

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(511, 290)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(30, 20, 463, 230))
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(self.widget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.inputCSVPath = QtWidgets.QLineEdit(self.splitter)
        self.inputCSVPath.setMinimumSize(QtCore.QSize(262, 28))
        self.inputCSVPath.setMaximumSize(QtCore.QSize(16777215, 28))
        self.inputCSVPath.setObjectName("inputCSVPath")
        self.gridLayout.addWidget(self.splitter, 1, 0, 1, 1)
        self.inputFileButton = QtWidgets.QPushButton(self.widget)
        self.inputFileButton.setMaximumSize(QtCore.QSize(100, 28))
        self.inputFileButton.setObjectName("inputFileButton")
        self.gridLayout.addWidget(self.inputFileButton, 1, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(436, 13, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 6, 0, 1, 2)
        self.label_3 = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.outputCSVPath = QtWidgets.QLineEdit(self.widget)
        self.outputCSVPath.setMinimumSize(QtCore.QSize(262, 28))
        self.outputCSVPath.setMaximumSize(QtCore.QSize(16777215, 28))
        self.outputCSVPath.setObjectName("outputCSVPath")
        self.gridLayout.addWidget(self.outputCSVPath, 5, 0, 1, 1)
        self.StatusMessage = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.StatusMessage.setFont(font)
        self.StatusMessage.setText("")
        self.StatusMessage.setObjectName("StatusMessage")
        self.gridLayout.addWidget(self.StatusMessage, 4, 1, 1, 1)
        self.API_Key = QtWidgets.QLineEdit(self.widget)
        self.API_Key.setEnabled(True)
        self.API_Key.setMinimumSize(QtCore.QSize(0, 28))
        self.API_Key.setObjectName("API_Key")
        self.gridLayout.addWidget(self.API_Key, 3, 0, 1, 2)
        self.outputFileButton = QtWidgets.QPushButton(self.widget)
        self.outputFileButton.setMaximumSize(QtCore.QSize(100, 28))
        self.outputFileButton.setObjectName("outputFileButton")
        self.gridLayout.addWidget(self.outputFileButton, 5, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.calculateButton = QtWidgets.QPushButton(self.widget)
        self.calculateButton.setEnabled(True)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.calculateButton.setFont(font)
        self.calculateButton.setObjectName("calculateButton")
        self.gridLayout.addWidget(self.calculateButton, 7, 0, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        # Connection functions
        self.calculateButton.clicked.connect(self.calculateTravelTimes)
        self.outputFileButton.clicked.connect(self.outputFileButtonClicked)
        self.inputFileButton.clicked.connect(self.inputFileButtonClicked)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.inputFileButton.setText(_translate("MainWindow", "Select File"))
        self.label_3.setText(_translate("MainWindow", "Output CSV"))
        self.label_2.setText(_translate("MainWindow", "Google Maps API Key"))
        self.outputFileButton.setText(_translate("MainWindow", "Select File"))
        self.label.setText(_translate("MainWindow", "Input CSV"))
        self.calculateButton.setText(_translate("MainWindow", "Calculate"))

    def inputFileButtonClicked(self):
        filename, filter = QFileDialog.getOpenFileName(caption='Select File', filter='CSV File (*.csv)')

        if filename:
            if filename[-4:] != '.csv':
                filename += '.csv'
        self.inputCSVPath.setText(filename)

    def outputFileButtonClicked(self):
        filename, filter = QFileDialog.getSaveFileName(caption='Save File', filter='CSV File (*.csv)')

        if filename:
            if filename[-4:] != '.csv':
                filename += '.csv'
        self.outputCSVPath.setText(filename)

    def checkSetupErrors(self):
        # Handles errors involving empty fields
        error_dialog = QtWidgets.QMessageBox()
        error_dialog.setIcon(QMessageBox.Warning)

        if self.inputCSVPath.text() == '' or self.outputCSVPath.text() == '':
            error_dialog.setText('Invalid CSV path name(s)')
            error_dialog.setWindowTitle("Error")
            error_dialog.exec_()
            return

        elif self.API_Key.text() == '':
            error_dialog.setText('No API key present')
            error_dialog.setWindowTitle("Error")
            error_dialog.exec_()
            return

    def calculateTravelTimes(self):
        self.checkSetupErrors()

        API_key = self.API_Key.text()
        input_filename = self.inputCSVPath.text()
        output_filename = self.outputCSVPath.text()
        df = pd.read_csv(input_filename)

        # CALCULATION BEGINS HERE
        df['Transit Mode'] = df.apply(assign_travel_mode, axis=1)

        # Create separate dataframes for each travel mode
        bicycling_df = df[df['Transit Mode'] == 'bicycling']
        driving_df = df[df['Transit Mode'] == 'driving']
        walking_df = df[df['Transit Mode'] == 'walking']
        bus_df = df[df['Transit Mode'] == 'bus']
        train_df = df[df['Transit Mode'] == 'train']
        other_df = df[df['Transit Mode'] == 'other']

        # Create Google links for all modes
        bike_links = create_links(bicycling_df, "bicycling", API_key)
        drive_links = create_links(driving_df, "driving", API_key)
        walk_links = create_links(walking_df, "walking", API_key)
        bus_links = create_links(bus_df, "bus", API_key)
        train_links = create_links(train_df, "train", API_key)
        other_links = create_links(other_df, "Not Available", API_key) # Will default to driving

        # Get distances and times, then merge them into one large dataframe
        bicycling_df = get_distance_and_time(bike_links, bicycling_df)

        if bicycling_df is None:
            return

        driving_df = get_distance_and_time(drive_links, driving_df)
        walking_df = get_distance_and_time(walk_links, walking_df)
        bus_df = get_distance_and_time(bus_links, bus_df)
        train_df = get_distance_and_time(train_links, train_df)
        other_df = get_distance_and_time(other_links, other_df)

        # Switch biking distances of more than 10 miles to driving
        bike_to_drive_df = bicycling_df[bicycling_df['Miles'] > 10]
        bicycling_df = bicycling_df[bicycling_df['Miles'] <= 10]

        bike_to_drive_df['Transit Mode'] = bike_to_drive_df['Transit Mode'].str.replace("bicycling", "driving")
        bike_to_drive_links = create_links(bike_to_drive_df, "driving", API_key)
        new_drive_df = get_distance_and_time(bike_to_drive_links, bike_to_drive_df)

        # Combine and sort results
        all_df = [bicycling_df, driving_df, walking_df, bus_df, train_df, other_df, new_drive_df]

        new_df = pd.concat(all_df)
        new_df = new_df.sort_values(by=['FID'], ascending=True)
        new_df.to_csv(output_filename, index=False)

        success_dialog = QtWidgets.QMessageBox()
        success_dialog.setText('Your travel times and distances have successfully been saved.')
        success_dialog.setWindowTitle("Success")
        success_dialog.exec_()

def assign_travel_mode(row):

    if (row['Primary_Mo'] == "Bike" or row['Primary_Mo'] == "Skate, skateboard, or scooter" or
        row['Primary_Mo'] == "Electric-assist bike (e-bike)" or
        row['Primary_Mo'] == "Electric-assist scooter or skateboard (e-scooter or e-skateboard)"):
        return 'bicycling'

    elif (row['Primary_Mo'] == "Carpool and/or vanpool with others going to campus" or
        row['Primary_Mo'] == "Drive alone in a car (or other vehicle)" or
        row['Primary_Mo'] == "Get dropped off by a friend or family (the driver continues on elsewhere)" or
        row['Primary_Mo'] == "Lyft, Uber, or other ride-hailing service" or
        row['Primary_Mo'] == "Motorcycle or Vespa-like scooter"):
        return 'driving'

    elif row['Primary_Mo'] == "Walk (or wheelchair)":
        return 'walking'

    elif row['Primary_Mo'] == "Bus and/or shuttle":
        return 'bus'

    elif row['Primary_Mo'] == "Train and/or light rail":
        return 'train'

    else:
        return 'other'

def create_links(df, mode, API_key):
    '''Separates each DataFrame into batches of 25 in order for Google Maps to accept API calls, then create string of coordinates for each API call. Afterwards, create links for API calls'''

    str_array = np.array([])
    coordinate_str = ''

    for i in range(len(df)):
        coordinate_str += str(df['Y'].iloc[i]) + ',' +  str(df['X'].iloc[i]) # Google Maps uses a flipped version of X, Y coordinates than ArcGIS

        if (i + 1) % max_dest == 0:
            str_array = np.append(str_array, coordinate_str)
            coordinate_str = ''
            continue

        elif i == len(df) - 1:
            str_array = np.append(str_array, coordinate_str)
            break

        else:
            coordinate_str += '|'

    api_links = np.array([])

    for i in range(len(str_array)):
        API_call = API_link + \
                 '&origins=' + origin + \
                 '&destinations=' + str(str_array[i]) + \
                 '&key=' + API_key

        if mode == "bus" or mode == "train":
          API_call = API_call + '&transit_mode=' + mode

        elif mode == "driving" or mode == "walking" or mode == "bicycling":
          API_call = API_call + '&mode=' + mode

        api_links = np.append(api_links, API_call)

    return api_links

def get_distance_and_time(link_array, df):
    pd.options.mode.chained_assignment = None  # default='warn'
    distance_array = np.array([], dtype='int16') # distances will be in meters
    time_array = np.array([], dtype='int16') # times will be in seconds

    error_dialog = QtWidgets.QMessageBox()
    error_dialog.setIcon(QMessageBox.Warning)

    for i in range(len(link_array)):
        r = requests.get(url = link_array[i])
        data = r.json()

        # Handling Google API status codes
        if data['status'] == 'REQUEST_DENIED':
            error_dialog.setText('API key not authorized')
            error_dialog.setWindowTitle("Error")
            error_dialog.exec_()
            return
        elif data['status'] == 'OVER_DAILY_LIMIT':
            error_dialog.setText('API key is invalid')
            error_dialog.setWindowTitle("Error")
            error_dialog.exec_()
            return
        elif data['status'] == 'INVALID_REQUEST':
            error_dialog.setText('Google could not process one or more addresses in the input CSV file')
            error_dialog.setWindowTitle("Error")
            error_dialog.exec_()
            return

        for j in range(len(data['rows'][0]['elements'])):
          try:
            distance_array = np.append(distance_array, data['rows'][0]['elements'][j]['distance']['value'])
          except:
            distance_array = np.append(distance_array, np.nan)
            time_array = np.append(time_array, np.nan)
            continue
          time_array = np.append(time_array, data['rows'][0]['elements'][j]['duration']['value'])

    df['Miles'] = distance_array * 0.000621371 # Convert from meters to miles
    df['Duration (in minutes)'] = time_array / 60 # Convert from seconds to minutes

    return df

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    window.setWindowTitle("Campus Travel Distance Calculator")
    window.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
