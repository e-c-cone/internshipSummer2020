#Tester Class - Elizabeth Cone
#06 26 2020

import argparse
import sys
import pathlib
from time import sleep
import serial
import serial.tools.list_ports

from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append( str(current_dir) + '/../' )

from pykeigan import usbcontroller
from pykeigan import utils
from pykeigan import *

class Tester(): #Tester Object ------------------------------------------------------------------------------------
    
    def __init__(self):
        print("Tester created. ")
        
    def connect(self, port):
        if sys.platform.startswith('win'): #detects if platform is windows and uses the input port
            # !attention assumes pyserial 3.x
            self.dev = usbcontroller.USBController(port, baud=115200) #run select port if windows
            print("Connected.")
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'): #if platform is linux, uses default linux port for keiganmotor
            # this excludes your current terminal "/dev/tty"
            self.dev = usbcontroller.USBController("/dev/serial/by-id/usb-FTDI_FT230X_Basic_UART_DM00KIWP-if00-port0",False)
            print("Connected.")
        self.dev.enable_action()
        self.dev.set_notify_pos_arrival_settings(False, 0, 0) #avoids position read errors
        self.dev.set_led(1, 255, 255, 255)
        self.dev.enable_continual_motor_measurement()
        self.dev.enable_continual_imu_measurement()
        self.dev.set_motor_measurement_interval(2)
        self.dev.run_at_velocity(3) #runs for troubleshooting -- can see that the motor connected
        sleep(1)
        self.dev.stop_motor()

    #The below testing functions were for BEFORE I had the graphs display in real time -- they no longer get called in the TestMain program
    ''' OLD TEST FUNCTIONS ----------------------------------------------------------------------    
    def testVelocity(self, testVal, vel, timeV, timeRV): #trange = range of testing values, vel = list to append to
        self.dev.set_led(1, 100, 0, 230)
        timer_to_append = 0.0
        if len(timeRV) != 0:
            timer_to_append = timeRV[-1] #timer to append to time list for the graph
        timer = 0.0 #loop timer
        self.dev.run_at_velocity(x)
        while (timer <= 4.0):
            sleep(.2)
            timer += .2
            timer_to_append += .2
            vel.append(self.dev.read_motor_measurement()["velocity"])
            timeV.append(timer_to_append)        
            
    def testTorque(self, trange, tor, timeT, timeRT): #trange = range of testing values, tor = list to append to
        self.dev.set_led(1, 0, 200, 100)
        self.dev.run_forward()
        timer_to_append = 0.0
        if len(timeRT) != 0:
            timer_to_append = timeRT[-1] #timer to append to time list for the graph
        for x in trange:
            self.dev.set_max_torque(x)
            timer = 0.0 #loop timer
            while (timer <= 4.0):
                sleep(.2)
                timer += .2
                timer_to_append += .2
                tor.append(self.dev.read_motor_measurement()["torque"])
                timeT.append(timer_to_append)
        self.dev.stop_motor()
        self.dev.set_max_torque(10)
            
    def testPosition(self, trange, pos, timeP, timeRP):
        self.dev.set_led(1, 200, 0, 100)
        self.dev.preset_position(0)
        timer_to_append = 0.0
        if len(timeRP) != 0:
            timer_to_append = timeRP[-1] #timer to append to time list for the graph
        for x in trange:
            timer = 0.0 #loop timer
            self.dev.move_to_pos(x,5)
            sleep(.5)
            while (self.dev.read_motor_measurement()["velocity"] >= 0):
                sleep(.2)
                timer += .2
                timer_to_append += .2
                pos.append(self.dev.read_motor_measurement()["position"])
                timeP.append(timer_to_append)
        self.dev.stop_motor()

    End old functions --------------------------------------------------------------------''' 

    def findError(self, desired, measured, dtime, mtime): #need to perfect this -- currently returns large error due to test transitions
        i = 0
        j = 0
        errorTotal = 0.0
        
        if (len(dtime)==0 or len(mtime) == 0): # empty case
            return ("Error: no data received. ")
        
        elif len(dtime) == 1:               # one point case
            for x in mtime:
                errorTotal += x-desired[0]                

        else: #all other cases
            while i < (len(dtime)-1): #since the error needs to be compared between theoretical and measured points AT THE SAME TIME REFERENCES, but the time arrays are different length, needed to traverse through 2 loops
                while (round(dtime[i+1], 1) != round(mtime[j],1)): #while the measured time is BETWEEN theoretical time values, test the same theoretical value vs. all the measured values
                    errorTotal += measured[j]-desired[0] #calculate TOTAL sum 'off' data
                    j+=1
                i+=1
            while (j != len(mtime)-1): #goes through the LAST theoretical value vs. measured values loop (to avoid index out of bounds error)
                    errorTotal += measured[j]-desired[i]
                    j+=1
    
        return round((errorTotal/len(measured)), 5) #divide sum of error by number of data points rounded to the 5th decimal and return
                
    def read_baud(self):
        return self.dev.read_baud_rate() #RETURNS ERROR -- 'read baud does not exist'

    def set_baud(self, baud):     #this causes read errors -- i dont know why and I couldnt fix it :(  
        self.dev.set_baud_rate(baud)
        self.dev.save_all_registers()
        self.dev.reboot()
        #self.dev.enable_action()
        #self.dev.enable_continual_motor_measurement() -- I put these two functions in to try and troubleshoot the read errors, but they didnt fix anything
        #self.dev.set_notify_pos_arrival_settings(False, 0, 0)
        self.dev.run_at_velocity(5)
        sleep(1)
        self.dev.stop_motor()

    #All the functions below were to extend the controller functionality into the tester object, after I moved the testing functions into the main so that I could update the graphs as the tests ran.
    def stopMotor(self):
        self.dev.stop_motor()

    def setZeroPos(self):
        self.dev.preset_position(0)

    def maxTorque(self, torque):
        self.dev.set_max_torque(torque)

    def moveToPos(self, pos):
        self.dev.move_to_pos(pos, 6)

    def run_at_v(self, vel):
        self.dev.run_at_velocity(vel)

    def get_pos_d(self):
        return self.dev.read_position_d()

    def set_pos_d(self, x):
        self.dev.set_position_d(x)
        
    def get_pos_p(self):
        return self.dev.read_position_p()
        
    def set_pos_p(self, x):
        self.dev.set_position_p(x)
        
    def get_pos_i(self):
        return self.dev.read_position_i()
        
    def set_pos_i(self, x):
        self.dev.set_position_i(x)
        
    def get_speed_d(self):
        return self.dev.read_speed_d()
        
    def set_speed_d(self, x):
        self.dev.set_speed_d(x)
        
    def get_speed_p(self):
        return self.dev.read_speed_p()
        
    def set_speed_p(self, x):
        self.dev.set_speed_p(x)
         
    def set_speed_i(self, x):
        self.dev.set_speed_i(x)
        
    def get_speed_i(self):
        return self.dev.read_speed_i()

    def get_qc_p(self):
        return self.dev.read_qcurrent_p()

    def get_qc_i(self):
        return self.dev.read_qcurrent_i()

    def get_qc_d(self):
        return self.dev.read_qcurrent_d()

    def resetPID(self):
        self.dev.reset_all_pid()
        
    def measureVel(self):
        return self.dev.read_motor_measurement()["velocity"]

    def measurePos(self):
        return self.dev.read_motor_measurement()["position"]

    def measureTor(self):
        return self.dev.read_motor_measurement()["torque"]
            
                     
        
        
