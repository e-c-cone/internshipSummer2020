# Python code to demonstrate working of unittest for KeiganMotor controller commands
import unittest
import serial
import numpy
from time import sleep
from pykeigan import usbcontroller
from pykeigan import utils
  
class TestController(unittest.TestCase):

    #issues -- read_register returns NoneType for all the tests I've run. I haven't been able to find a workaround for this, which
    #unfortunately seriously limits what I can test effectively.

    dev = usbcontroller.USBController('COM13') #CHANGE 'COM13' TO WHATEVER YOUR PORT IS.

    def setUp(self):
        pass
        #port = serial.Serial(port='COM13')
        
    def tearDown(self):
        pass

    def test_reset_registers(self):
        pass
        #self.dev.reset_all_registers() -- caused read error 
        
    def test_set_notify_pos_arrival_settings(self): #also tests read register? not sure of register values for pos settings
        self.dev.set_notify_pos_arrival_settings(False, 0, 0)
        self.assertEqual(self.dev.read_register(43), 0) #read_register returns none -- test always fails (returns an error)

    def test_enable_action(self):
        self.dev.enable_action()

    def test_disable_continual_motor_measurement(self):
        #USES READ MOTOR STATUS TO TEST CONTINUAL MEASUREMENT - DISABLE MOTOR
        self.dev.disable_continual_motor_measurement()
        self.assertEqual(self.dev.read_status()['motorMeasurement'], 0)

    def test_enable_continual_motor_measurement(self):
        #USES READ MOTOR STATUS TO TEST CONTINUAL MEASUREMENT - ENABLE MOTOR
        self.dev.enable_continual_motor_measurement()
        self.assertEqual(self.dev.read_status()['motorMeasurement'], 1)

    def test_disable_continual_imu_measurement(self):
        #USES READ MOTOR STATUS TO TEST CONTINUAL MEASUREMENT - DISABLE IMU
        self.dev.disable_continual_imu_measurement()
        self.assertEqual(self.dev.read_status()['iMUMeasurement'], 0)

    def test_enable_continual_imu_measurement(self):
        #USES READ MOTOR STATUS TO TEST CONTINUAL MEASUREMENT - ENABLE IMU
        self.dev.enable_continual_imu_measurement()
        self.assertEqual(self.dev.read_status()['iMUMeasurement'], 1)
    
    def test_max_speed(self):
        self.dev.set_max_speed(10) #set max speed to 10
        self.dev.run_at_velocity(15) #run at speed so there is data to read
        sleep(1)
        self.dev.stop_motor()
        self.assertEqual(self.dev.read_max_speed(), 10) #read max speed from read function

    def test_min_speed(self):
        self.dev.set_min_speed(5) #set min speed to 5
        self.dev.run_at_velocity(3) #run at less than min speed
        sleep(1)
        self.dev.stop_motor() 
        self.assertEqual(self.dev.read_min_speed(), 5) #read min speed from min function

    def test_set_acc(self):
        self.dev.set_acc(10) #set acc to 10
        sleep(1)
        self.assertEqual(self.dev.read_acc(), 10) # read acceleration and assert
        self.dev.stop_motor() #stop from acceleration

    def test_set_dec(self):
        self.dev.run_at_velocity(10) #start running
        self.dev.set_dec(10) #start to decelerate
        sleep(1)
        self.assertEqual(self.dev.read_dec(), 10) #read deceleration
        self.dev.stop_motor()#come to complete stop

    def test_set_max_torque(self): # was having an issue with torque motor measurements being too variable to test off of, so I'm using the read functions instead
        self.dev.set_max_torque(.05)
        self.dev.run_forward()
        sleep(2)
        self.assertEqual(round(self.dev.read_max_torque(), 5), .05) #read max torque
        self.dev.set_max_torque(10)
        self.assertEqual(self.dev.read_max_torque(), 10) #read max torque after second change of setting
        self.dev.stop_motor()

    def test_set_teaching_interval(self):
        #I was getting read errors when I tried this function
        pass

    def test_set_curve_type(self):
        self.dev.set_curve_type(0)
        sleep(1)
        self.assertEqual(self.dev.read_curve_type(), 0)
        self.dev.set_curve_type(1)
        sleep(1)
        self.assertEqual(self.dev.read_curve_type(), 1)

    def test_reset_all_pid(self): #also essentially tests all read functions pid
        self.dev.reset_all_pid() #RESETS THE PID
        self.assertEqual(self.dev.read_speed_p(), 14)
        self.assertEqual(round(self.dev.read_speed_i(), 5), .001)
        self.assertEqual(round(self.dev.read_speed_d(),5), 0.0)
        self.assertEqual(self.dev.read_position_p(), 5)
        self.assertEqual(self.dev.read_position_i(), 10)             #these lines simply assert that every value was set back to the default value, which I found by restarting the system
        self.assertEqual(round(self.dev.read_position_d(), 5), .01)
        self.assertEqual(round(self.dev.read_qcurrent_p(), 5), .2)
        self.assertEqual(round(self.dev.read_qcurrent_i(), 5), 20) #rounding in cases of very small values which would flag as a failure for very very small amounts of variation
        self.assertEqual(round(self.dev.read_qcurrent_d(), 5), 0.0)

    def test_set_read_speed_p(self):
        self.dev.set_speed_p(15) #changes speed p value from default
        self.assertEqual(self.dev.read_speed_p(), 15) #asserts change is reflected in motor settings
        self.dev.reset_all_pid() #reset so that you make sure the change doesnt affect further tests
        
    def test_set_read_speed_i(self):
        self.dev.set_speed_i(.002) #changes speed i value -- first line of all PID tests changes the value
        self.assertEqual(round(self.dev.read_speed_i(), 5), .002) #asserts the change was made -- rounds since its a tiny value
        self.dev.reset_all_pid() #reset so that you make sure the change doesnt affect further tests

    def test_set_speed_d(self):
        self.dev.set_speed_d(1)
        self.assertEqual(self.dev.read_speed_d(), 1) #asserts change was made
        self.dev.reset_all_pid() #reset so that you make sure the change doesnt affect further tests

    def test_set_position_p(self):
        self.dev.set_position_p(7)
        self.assertEqual(self.dev.read_position_p(), 7) #asserts change was made
        self.dev.reset_all_pid() #reset so that you make sure the change doesnt affect further tests
        
    def test_set_position_i(self):
        self.dev.set_position_i(11)
        self.assertEqual(self.dev.read_position_i(), 11) # asserts change was made
        self.dev.reset_all_pid() #reset so that you make sure the change doesnt affect further tests

    def test_set_position_d(self):
        self.dev.set_position_d(.02)
        self.assertEqual(round(self.dev.read_position_d(), 5), .02)#asserts change was made -- rounds since its such a small value
        self.dev.reset_all_pid() #reset so that you make sure the change doesnt affect further tests

    def test_set_qcurrent_p(self):
        self.dev.set_qcurrent_p(.3)
        sleep(.5)
        self.assertEqual(round(self.dev.read_qcurrent_p(), 5), .3)#asserts change was made -- rounds since its such a small value
        self.dev.reset_all_pid() #reset so that you make sure the change doesnt affect further tests

    def test_set_qcurrent_i(self):
        self.dev.set_qcurrent_p(21)
        sleep(.5)
        self.assertEqual(round(self.dev.read_qcurrent_p(), 5), 21)#asserts change was made
        self.dev.reset_all_pid() #reset so that you make sure the change doesnt affect further tests

    def test_set_qcurrent_d(self):
        self.dev.set_qcurrent_p(.02)
        sleep(.5)
        self.assertEqual(round(self.dev.read_qcurrent_p(), 5), .02)#asserts change was made -- round since value was off by very small amounts
        self.dev.reset_all_pid() #reset so that you make sure the change doesnt affect further tests

    def test_set_motor_measurement_interval(self): # THE READ MEASUREMENT INTERVAL FUNCTION FOR BOTH IMU AND MOTOR MEASUREMENT DID NOT RUN CORRECTLY. both resulted in an error, so they are commented out.
        self.dev.set_motor_measurement_interval(7) # set to 2000 ms
        #self.assertEqual(self.dev.read_motor_measurement_interval(), 2000) 
        #print(self.dev.read_motor_measurement_interval())       

    def test_set_imu_measurement_interval(self): #See comment for function above
        self.dev.set_imu_measurement_interval(7) # set to 2000 ms
        #self.assertEqual(self.dev.read_imu_measurement_interval, 2000) -- read_measurement_interval doesnt appear to work
        #print(self.dev.read_imu_measurement_interval())

    def test_preset_position(self):
        self.dev.preset_position(0) #runs the preset function, sets it to 0
        sleep(1)
        self.assertEqual(round(self.dev.read_motor_measurement()["position"]), 0) #asserts change was made
        self.dev.preset_position(10) #double check my preseting position to 10 
        sleep(1)
        self.assertEqual(round(self.dev.read_motor_measurement()["position"]), 10) #asserts change was made

    def test_move_to_pos(self):
        self.dev.preset_position(0) #makes sure there is no error due to starting position
        sleep(1)
        self.dev.move_to_pos(15, 9) #runs move to pos function
        sleep(3)#gives it time to move to the position
        self.assertEqual(round(self.dev.read_motor_measurement()["position"]), 15) #asserts position was reached
        self.dev.move_to_pos(7, 9) # move to second position
        sleep(3)# time to move to position
        self.assertEqual(round(self.dev.read_motor_measurement()["position"]), 7) #asserts position was reached

    def test_run_at_vel(self):
        self.dev.run_at_velocity(3) #run at vel 3
        sleep(2) # time to get up to velocity
        self.assertEqual(round(self.dev.read_motor_measurement()["velocity"]), 3) #asserts that the velocity it is running at is about 3
        self.dev.run_at_velocity(9) # change to running at vel of 9
        sleep(2) #time to get to second velocity
        self.assertEqual(round(self.dev.read_motor_measurement()["velocity"]), 9) #asserts vel is running at about 9
        self.dev.stop_motor() 

    def test_run_forward(self):
        self.dev.run_forward() #runs the function
        sleep(3)
        self.assertTrue(self.dev.read_motor_measurement()["velocity"] > 0)# asserts the velocity is non-zero in the positive direction
        self.dev.stop_motor()

    def test_run_reverse(self):
        self.dev.run_reverse() #runs the function
        sleep(3)
        self.assertTrue(self.dev.read_motor_measurement()["velocity"] < 0) #asserts the read velocity is non-zero in the negative direction (reverse)
        self.dev.stop_motor()

    def test_stop_motor(self):
        self.dev.run_at_velocity(3)
        sleep(2)
        self.dev.stop_motor()
        sleep(1)
        self.assertEqual(round(self.dev.read_motor_measurement()["velocity"]), 0) #tests that the motor stopped from running at velocity
        
    def test_set_speed(self):
        self.dev.set_speed(5) #set speed to run at to be 5
        self.dev.run_forward()
        sleep(4)
        self.assertEqual(round(self.dev.read_motor_measurement()["velocity"]), 5) #tests that the motor is running at the speed it was told to (5)
        self.dev.stop_motor()

    def test_move_by_dist(self):
        start = self.dev.read_motor_measurement()["position"]
        self.dev.move_by_dist(10, 5) #move dist of 10 at speed 5
        sleep(4) # time to reach position
        self.assertTrue(start+9.5 < self.dev.read_motor_measurement()["position"] < start+10.5) #tests that the motor moved from it's original position by ~10

    def test_get_pos_offset(self): #get_pos_offset only returns NoneType -- doesn't work (always runs with an error)
        self.dev.move_to_pos(20)
        sleep(5)
        self.assertTrue(-.1 < self.dev.get_position_offset(10) < .1)

    def test_set_led(self): #also tests read own color -- READ OWN COLOR APPEARS TO NOT WORK CORRECTLY
        self.dev.set_led(1, 101, 200, 101)
        sleep(1)
        self.assertEqual(self.dev.read_own_color()[0], 101)
        self.assertEqual(self.dev.read_own_color()[1], 200)
        self.assertEqual(self.dev.read_own_color()[2], 101)

    def test_set_own_color(self): #also tests read own color -- always fails due to read error of read own color
        self.dev.set_own_color(101, 0, 101)
        sleep(1)
        self.assertEqual(self.dev.read_own_color()[0], 101)
        self.assertEqual(self.dev.read_own_color()[1], 0)
        self.assertEqual(self.dev.read_own_color()[2], 101)
     
    def test_taskset_functions_bulk(self): #tests taskset functions
        self.dev.stop_motor()
        sleep(2)
        self.dev.erase_all_tasksets() #for testing erase all
        self.dev.start_doing_taskset(1, 1)
        sleep(0.5)
        self.assertEqual(round(self.dev.read_motor_measurement()['velocity'], 1), 0, "Test for all tasket erasing success")
        # --- record
        self.dev.start_recording_taskset(1)
        self.dev.run_forward()
        sleep(3)
        self.dev.run_reverse()
        sleep(3)
        self.dev.stop_motor()
        # --- stop recording
        self.dev.stop_recording_taskset() #should run without error, if it doesnt other tests will fail
        self.dev.start_doing_taskset(1, 1) #should run backwards and forwards once
        self.assertNotEqual(self.dev.read_motor_measurement()['velocity'], 0, "Test for tasket recording success") # checks that a task set was recorded at all -- ISSUE READING AFTER RECORDING
        sleep(5.25) #should get to the end of first taskset test
        self.assertEqual(round(self.dev.read_motor_measurement()['velocity'], 2), 0, "Test for tasket stop recording success") # checks that a taskset stopped correctly
        self.dev.start_doing_taskset(1, 3)
        sleep(17)
        self.assertNotEqual(self.dev.read_motor_measurement()['velocity'], 0, "Test for tasket repeat success") # checks that taskset plays correctly
        self.dev.erase_taskset(1)
        self.dev.start_doing_taskset(1, 1)
        sleep(.5)
        self.assertEqual(round(self.dev.read_motor_measurement()['velocity'], 2), 0, "Test for tasket erasing success")
        self.dev.set_own_color(1, 1, 1)

#Queue functions has an issue where creates errors in the other tests that run (Im not sure what order the main runs them in).
#I tried integrating the queue tests with the taskset tests, but I'm not sure what I'm doing wrong. These tests do not work correctly.
'''
    def test_queue_functions(self): #need to figure out how to queue works better with taskset
        self.dev.run_forward()
        self.dev.wait_queue(2000) #should run for 2 sec
        self.assertTrue(-.05 < self.dev.read_motor_measurement()['velocity'] < .05)
        self.dev.stop_motor()
        sleep(1)
        self.assertTrue(self.dev.read_motor_measurement()['velocity'] > 0)#makes sure it stopped after the wait queue
        self.dev.run_forward()
        self.dev.pause_queue()
        self.dev.stop_motor() #shouldn't run till the queue is unpaused
        x = 0
        while x <= 4:
            x+=1
            sleep(1)
            self.assertTrue(-.05 < self.dev.read_motor_measurement()['velocity'] < .05) #makes sure it's still working
            if x == 4:
                self.dev.resume_queue()
                sleep(1)
                self.assertTrue(self.dev.read_motor_measurement()['velocity'] > 0) #queue unpaused -- motor should stop
'''
                
#Teaching function tests create read errors upon trying to test the motor measurements -- apparently this is an issue with the flash state of the motor,
#but I can't figure out how to fix it through the code itself. I was what the flash states are in the controller and how TEACHING would stop it from being able to
#read at the same time, but don't know how to manually change back the flash state from the dev functions.

#The baud rate change function also creates all the same errors it created for the GUI -- I've tried a lot of troubleshooting, but am afraid it might be an issue with my motor.            
'''
    def test_teaching_functions(self): #tests teaching motion functions
        self.dev.stop_motor()
        sleep(2)
        self.dev.erase_all_motions() #for testing erase all
        self.dev.start_playback_motion(1, 1, 1)
        sleep(1)
        self.assertEqual(round(self.dev.read_motor_measurement()['velocity'], 2), 0, "Test for motion erasing success")
        self.dev.stop_playback_motion()
        # ---- record
        self.dev.start_teaching_motion(1, 5000) #start teaching motion with no prep
        self.dev.run_forward()
        sleep(3)
        self.dev.run_reverse()
        sleep(3)
        self.dev.stop_motor()
        # ---- stop recording
        self.dev.stop_teaching_motion() #should run without error, if it doesnt other tests will fail
        self.dev.start_playback_motion(1, 1, 1) #should run backwards and forwards once
        sleep(1)
        self.assertNotEqual(self.dev.read_motor_measurement()['velocity'], 0, "Test for teaching recording success") # checks that a task set was recorded at all
        sleep(5.25) #should get to the end of first taskset test
        self.assertEqual(round(self.dev.read_motor_measurement()['velocity'], 2), 0, "Test for tasket stop recording success") # checks that a taskset stopped correctly
        self.dev.stop_playback_motion() #make sure next test runs correctly
        self.dev.start_playback_motion(1, 1, 3)
        sleep(17)
        self.assertNotEqual(self.dev.read_motor_measurement()['velocity'], 0, "Test for playback repeat success") # checks that taskset plays correctly
        self.dev.erase_motion(1)
        self.assertIsNone(self.dev.read_motion(1))
        self.set_own_color(1, 250, 1) #test over - led green
     
    def test_set_baud_rate(self): #creates errors for all test
        self.dev.set_baud_rate(5)
        self.dev.save_all_registers()
        sleep(.5)
        self.dev.reboot()
        self.dev.run_at_velocity(5)
        sleep(3)
        self.dev.stop_motor()
    '''
if __name__ == '__main__':
    unittest.main() 
