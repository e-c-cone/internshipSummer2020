## Keigan Internship 2020 -- Testing Programs README

For the included programs to work, you will need PyQt5, pyserial, pyqtgraph and the pykeigan libraries installed. 
The TestMain and Test_Class will need to be in the same folder, as well as the .ui files, which were generated using QtDesigner.
The TestMain will detect whether you are on Windows and need to select a port, or on Linux and will use the default port for the KeiganMotor.
* After selecting a port, one can change the PID settings and baud rate (currently throws errors) in the entry boxes and combo box on the right of the UI.
* To enter values to test into the velocity, torque and position test graphs, enter values one at a time into the corresponding entry box and hit enter.
* The ui will display what values are in queue to test.
* Clear will clear all measured values, graphs and queued values to test. You can also clear torque, vel and position individually.
* Testing all will run the values currently in each queue, running each test one after another.

The unittest program requires only the pykeigan and unittest libraries, but is incomplete. All issues and uses are commented out in the code.
