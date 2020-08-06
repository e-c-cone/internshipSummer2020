import argparse
import sys
import pathlib
from time import sleep
import Test_Class
import os
import serial.tools.list_ports
import serial
import statistics

from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

portChoice = ""
tester = Test_Class.Tester()

vel = []
pos = [] #values for graphs
tor = []

trangeV = []
trangeP = [] #lists for desired vs measured tests
trangeT = []

timeV = []
timeT = [] #timer for desired vs measured tests
timeP = []

timerangeV = []
timerangeT = [] # timer to space desired values with measured in graphs
timerangeP = []

dataCount = [] #array to collect benchmarkers in the data to make sure error can be calculated correctly

class MainWindow(QtWidgets.QMainWindow): #using pyqt5

    def runT(self): # Button functions to run on press------------------------------------------------
        count = 0.00 #reset counter
        self.torGraph.plot() #intial tor graph plotted
        for x in trangeT:
            tester.maxTorque(x) #set the max torque to whatever the appropriate value is in the testing array
            timerangeT.append(count) #append current count to the timer array for graphing theoretical values
            while (round(count,1) % 4.0 != 0) or (round(count) == 0.0): #switches testing next value every 4 seconds
                tor.append(abs(tester.measureTor())) #append the current torque measurement to the tor values array for graphing measured values
                timeT.append(count) #append time to the graph for the measured values graph
                self.torGraph.plot(timeT, tor, clear=True) #clear graph and graph next set of point in real time
                pg.QtGui.QApplication.processEvents() #refresh the GUI/graph
                sleep(.2)
                count+=.2 #move time forward and iterate counter
            count+=.2 #move counter so that the while loop doesnt get suck at forever 4sec point
        tester.maxTorque(10) #set max torque high so it doesnt affect other tests
        self.torGraph.plot(timerangeT, trangeT, pen=None, symbol = 'x') #graph theoretical values
        pg.QtGui.QApplication.processEvents() #refresh GUI
        self.eTor.setText("Avg Error: " + str(tester.findError(trangeT, tor, timerangeT, timeT))) #calculate error between theoretical to measured
        
    def runV(self):
        count = 0.00 #reset counter
        self.velGraph.plot() #initial vel graph plotted
        for x in trangeV:
            tester.run_at_v(x) #run at velocity of appropriate value in testing array
            timerangeV.append(count) #append time to timer array for graph of theoretical values
            while (round(count,1) % 3.0 != 0) or (round(count) == 0.0): #switches testing next value every 3 seconds
                vel.append(tester.measureVel()) #append measured velocity to array for graphing measured values
                timeV.append(count) #append measured time to time array for graphing measured values
                self.velGraph.plot(timeV, vel, clear=True) #clear graph and graph next time of measured points in real time
                pg.QtGui.QApplication.processEvents() #refresh GUI
                sleep(.2)
                count+=.2 #add to counter
            count+=.2 #add to counter so it doesnt get stuck at even 3 sec for while loop
        tester.stopMotor() 
        self.velGraph.plot(timerangeV, trangeV, pen=None, symbol = 'x') #graph theoretical values
        pg.QtGui.QApplication.processEvents() #refresh GUI
        self.eVel.setText("Avg Error: " + str(tester.findError(trangeV, vel, timerangeV, timeV)))#calculate error between theoretical and measured
            
        
    def runP(self):
        count = 0.00 #reset counter
        tester.setZeroPos() #reset position to 0 for calibration
        self.posGraph.plot() #initialize position graph
        for x in trangeP:
            tester.moveToPos(x) #moves to position value in testing array
            sleep(.2)
            timerangeP.append(count) #append time to theoretical graph's time array
            while (abs(round(tester.measureVel(),1)) > 0): #does not go to the next point until the velocity reaches zero (when motor reaches goal pos)
                pos.append(tester.measurePos()) #add measured position to measured values array for graphing
                timeP.append(count) #adds time to measured time array for graphing
                self.posGraph.plot(timeP, pos, clear=True) #graphs new points and clears old points (to graph in real time)
                pg.QtGui.QApplication.processEvents() #refresh GUI
                sleep(.2)
                count+=.2 #add to counter
            sleep(2)
            count+=2 #keeps motor at position for 2 seconds (to make the graph into a step graph of positions)
            pos.append(tester.measurePos()) #add same pos and +2 second time to graph array
            timeP.append(count)
        self.posGraph.plot(timeP, pos, clear=True) #plot last point after loop
        tester.stopMotor()
        self.posGraph.plot(timerangeP, trangeP, pen=None, symbol = 'x') #graph theoretical values
        pg.QtGui.QApplication.processEvents()# refresh gui
        self.ePos.setText("Avg Error: " + str(tester.findError(trangeP, pos, timerangeP, timeP))) #find error between theoretical and measured values
            

    def addT(self):
        trangeT.append(float(self.torEnter.text())) #add text from entry box as a float into the array of torque values to test
        self.listTor.setText(self.listTor.text() + " " + self.torEnter.text()) #add value to display of values to test in GUI
        self.torEnter.clear()
    def addP(self):
        trangeP.append(float(self.posEnter.text())) #add text from entry box as a float into the array of position values to test
        self.listPos.setText(self.listPos.text() + " " + self.posEnter.text()) #add value to display of values to test in GUI
        self.posEnter.clear()
    def addV(self):
        trangeV.append(float(self.velEnter.text())) #add text from entry box as a float into the array of velocity values to test
        self.listVel.setText(self.listVel.text() + " " + self.velEnter.text()) #add value to display of values to test in GUI
        self.velEnter.clear()

    def clearP(self):
        trangeP.clear() #clears array of position values to test
        timerangeP.clear() #clears theoretical time array
        timeP.clear()
        pos.clear() #clears array of measured values
        self.listPos.setText("Values to test: ") #resets displau
        self.posGraph.clear()
        self.ePos.setText("Avg Error: ")
    def clearV(self):
        trangeV.clear() #clears  array of vel values to test
        timerangeV.clear()
        timeV.clear()
        vel.clear()
        self.listVel.setText("Values to test: ") #resets display
        self.velGraph.clear()
        self.eVel.setText("Avg Error: ")
    def clearT(self):
        trangeT.clear() #clears array of torque values to test
        timerangeT.clear()
        timeT.clear()
        tor.clear()
        self.listTor.setText("Values to test: ") #resets display
        self.torGraph.clear()
        self.eTor.setText("Avg Error: ")

    def clearAll(self): #runs all clear functions
        self.clearT()
        self.clearV()
        self.clearP()
    def testAll(self): #runs all test functions sequentially
        self.runV()
        self.runP()
        self.runT()

    def setSP(self):
        tester.set_speed_p(float(self.setSpeedP.text())) #sets speed p value to whats in the entry box
        self.curSP.setText("Current: " + str(tester.get_speed_p())) #changes value in the display
        self.setSpeedP.clear() #clears the entry box
    def setSI(self):
        tester.set_speed_i(float(self.setSpeedI.text())) #sets speed i value
        self.curSI.setText("Current: " + str(tester.get_speed_i()))  #changes value in the display
        self.setSpeedI.clear() #clears the entry box
    def setSD(self):
        tester.set_speed_d(float(self.setSpeedD.text())) #sets speed d value
        self.curSD.setText("Current: " + str(tester.get_speed_d()))  #changes value in the display
        self.setSpeedD.clear() #clears the entry box

    def setPP(self):
        tester.set_pos_p(float(self.setPosP.text())) #sets the position p value to whats in the entry box
        self.curPP.setText("Current: " + str(tester.get_pos_p()))  #changes value in the display
        self.setPosP.clear() #clears the entry box
    def setPI(self):
        tester.set_pos_i(float(self.setPosI.text())) #sets the position i value
        self.curPI.setText("Current: " + str(tester.get_pos_i()))  #changes value in the display
        self.setPosI.clear() #clears the entry box
    def setPD(self):
        tester.set_pos_d(float(self.setPosD.text()))  #sets the position d value
        self.curPD.setText("Current: " + str(tester.get_pos_d()))  #changes value in the display
        self.setPosD.clear() #clears the entry box
        
    def reset_all_pid(self):
        tester.resetPID() #resets the pid for the tester
        self.curPP.setText("Current: " + str(tester.get_speed_p()))
        self.curPI.setText("Current: " + str(tester.get_speed_i()))
        self.curPD.setText("Current: " + str(tester.get_speed_d())) # updates the display for all PID values
        self.curSP.setText("Current: " + str(tester.get_pos_p()))
        self.curSI.setText("Current: " + str(tester.get_pos_i()))
        self.curSD.setText("Current: " + str(tester.get_pos_d()))

    def setBaudRate(self): # runs correctly, but results in erros afterwards
        print(self.baudCombo.currentText()[0])
        tester.set_baud(int(self.baudCombo.currentText()[0]))
        #self.currentBaud.setText("Current Baud Rate: " + str(tester.read_baud())) -- read baud 'doesnt exist', creates an error
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        #load in ui from qtdesigner
        uic.loadUi('window1.ui', self)

        self.reset_all_pid() #makes sure all PID is default on starting the program

        #self.currentBaud.setText("Current Baud Rate: " + str(tester.read_baud())) -- read baud 'doesnt exist' -- creates error

        #all functions below simply run the function in the argument once the specified component in the GUI is activated 
        self.velButton.clicked.connect(self.runV)
        self.torButton.clicked.connect(self.runT)
        self.posButton.clicked.connect(self.runP)

        self.clearVel.clicked.connect(self.clearV)
        self.clearTor.clicked.connect(self.clearT)
        self.clearPos.clicked.connect(self.clearP)

        self.torEnter.returnPressed.connect(self.addT)
        self.posEnter.returnPressed.connect(self.addP)
        self.velEnter.returnPressed.connect(self.addV)

        self.setSpeedP.returnPressed.connect(self.setSP)
        self.setSpeedI.returnPressed.connect(self.setSI)
        self.setSpeedD.returnPressed.connect(self.setSD)

        self.setPosP.returnPressed.connect(self.setPP)
        self.setPosI.returnPressed.connect(self.setPI)
        self.setPosD.returnPressed.connect(self.setPD)
        
        self.resetPID.clicked.connect(self.reset_all_pid)
        self.testAllB.clicked.connect(self.testAll)
        self.clearAllB.clicked.connect(self.clearAll)

        self.changeBaud.clicked.connect(self.setBaudRate) #this creates an error (read error) after running -- can only be fixed by reseting the motor

        #self.runRPID.clicked.connect(self.pid_reverse)
        #self.runFPID.clicked.connect(self.pid_forward)
        

class WindowLoader():
    def __init__(self):     
        self.dialog = uic.loadUi('popUp.ui') #sets the UI to be the popUp ui I made in qtdesigner
        self.dialog.show() #shows the dialog box
        portlist = serial.tools.list_ports.comports()
        if not portlist:
            print('No available port') #if no portlist, quits the program
            sys.exit()
        for port in portlist:
            self.dialog.portCombo.addItem(port.device) #adds detected ports to the drop down combo box in the dialog
        global tester
        self.dialog.accepted.connect(self.setPort) #upon hitting ok in the dialog box, connects the motor and starts the main program

    def setPort(self):
        portChoice = self.dialog.portCombo.currentText() # sets port choice to the selected port in the dialog box
        tester.connect(portChoice) #runs the connect function in the tester object
        mainW = MainWindow()
        mainW.show() #shows the main window
        sys.exit(app.exec_()) #execute the app00
    
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = WindowLoader() #starts the process of opening the windows (dialog then main window)
