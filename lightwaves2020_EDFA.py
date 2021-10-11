import sys
import os 
from PyQt5 import QtWidgets, uic
import paramiko
import threading
import time
import configparser
from PyQt5.QtCore import Qt 
import numpy as np




serial = 'serial name'
script = 'python3 EDFA.py'

cwd = os.path.dirname(os.path.realpath(__file__))
cwd = cwd + '\\lightwaves2020_EDFA.ui'

class Ui(QtWidgets.QMainWindow):
    
    def __init__(self):
        
        super(Ui, self).__init__()
        uic.loadUi(cwd, self)
        self.show()

        #Flag to prevent threads accessing the send_command() function at the same time
        self.input_flag = 0

        self.gain.valueChanged.connect(self.set_mode_val)

        self.drive_buttons.buttonClicked.connect(self.drive_mode)
        self.LOS_buttons.buttonClicked.connect(self.LOS_mode)


        self.LOS_alm_set.clicked.connect(lambda:self.alm_set(0))
        self.current_alm_set.clicked.connect(lambda:self.alm_set(1))
        self.temp_alm_set.clicked.connect(lambda:self.alm_set(2))
        



        #Set-up SSH connection
        self.ssh_setup() 

        #The first command sent is the serial address for the device we are connecting to
        self.send_command(serial, True)

        #Initialisation for multithreading
        self._event = threading.Event()
        self._thread = threading.Thread(target=self.listen, daemon=True)
        self._thread.start()
        


    
    #function creates the power enable box in the top-right corner of the GUI

    #Prompts the user bvefore exiting
    def closeEvent(self,event):
        result = QtWidgets.QMessageBox.question(self,
                      "Confirm Exit...",
                      "Are you sure you want to exit ?",
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)
        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            event.accept()
            #self.ssh.close()    #Closes the ssh connection to the raspberry pi


    #Displays 'set current' or 'set outpower' or 'set gain' for whichever driving mode is selected
    def drive_mode(self):
        if self.APC.isChecked():
            self.gain_label.setText('Set Output Power')
            self.gain_unit.setText('dBm')
            self.gain.setDecimals(2)
            self.gain.setRange(-25,25)
            self.gain.setValue(0)
            self.gain.setSingleStep(1)

        elif self.AGC.isChecked():

            self.gain_label.setText('Set Gain')
            self.gain_unit.setText('dB')
            self.gain.setDecimals(2)
            self.gain.setRange(5,25)
            self.gain.setValue(5)
            self.gain.setSingleStep(1)

        else:   #ACC

            self.gain_label.setText('Set Current')
            self.gain_unit.setText('mA')
            self.gain.setDecimals(1)
            self.gain.setRange(0,350)
            self.gain.setValue(0)
            self.gain.setSingleStep(10)


    #Sets the behaviour of the module in the event of a loss of signal
    def LOS_mode(self):
        if self.LOS_off.isChecked():
            self.set_command('set_los_swd off',True)
        elif self.LOS_on.isChecked():
            self.set_command('set_los_swd on',True)
        elif self.LOS_cp.isChecked():
            self.set_command('set_los_swd cp',True)


    #Determines the driving mode, then sends the appropriate command to the EDFA
    def set_mode_val(self):
        value = self.gain.value()

        if self.APC.isChecked():
            command = f'set_mode p {value}'
        elif self.AGC.isChecked():
            command = f'set_mode g {value}'
        else:
            command = f'set_mode c {value}'

        self.set_command(command, True)

    #Sets each alarm
    def alm_set(self, alm):
        
        if alm == 0:
            if self.LOS_alm_set.isChecked():
                self.LOS_alm_set.setText('On')
                command = 'set_los ' + str(self.LOS_alm_val.value())
            else:
                self.LOS_alm_set.setText('Off')
                command = 'set_los d'
            self.set_command(command, True)
            
        elif alm == 1:
            if self.current_alm_set.isChecked():
                self.current_alm_set.setText('On')
                command = 'set_alarm_ld_crnt ' + str(self.current_alm_val.value())
            else:
                self.current_alm_set.setText('Off')
                command = 'set_alarm_ld_crnt d'
            self.set_command(command, True)

        else:
            if self.temp_alm_set.isChecked():
                self.temp_alm_set.setText('On')
                command1 = 'set_alarm_tpump_lo ' + str(self.temp_alm_low.value())
                command2 = 'set_alarm_tpump_hi ' + str(self.temp_alm_high.value())
            else:
                self.temp_alm_set.setText('Off')
                command1 = 'set_alarm_tpump_lo d'
                command2 = 'set_alarm_tpump_hi d'
            self.set_command(command1, True)
            self.set_command(command2, True)


    

    #send the command to be sent, but first ensure the listening thread is complete
    def set_command(self, command, response):
        while True:
            if not self._event.is_set():
                self.input_flag = 0         #blocks the listening thread from running while sending a command
                data = self.send_command(command,response)
                #print(data)
                return data
        

    #Sends a command over serial
    #If the command receives a response it is returned
    def send_command(self, command, response):
        serial_command = 'msa::edfa>' + command + '\n'  
        
        self.stdin.write(serial_command)
        self.stdin.flush()

        line1 = str(self.stdout.readline()) #Ignore input line when reading
        if response:
            timeout = time.time() + 5       #Waits 5 seconds for a response then timesout
            while time.time() < timeout:
                line2 = str(self.stdout.readline())
                data = line2.splitlines()[0]
                self.input_flag = 1
                print(data)
                return data

            print('read line faliure')
        self.input_flag = 1
                
                
    #Establishes connection to raspberry pi
    #Ensure that the raspberry ip, username and password are correct
    def ssh_setup(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect('192.168.0.254', username='pi', password='raspberry', timeout=5)
            
            self.stdin, self.stdout, stderr = self.ssh.exec_command(script, get_pty=True)
                        
        except:
            print('Connection failed. \nCheck connection and try again')
            quit()


    #A seperate thread that continously requests the EDFA monitor values
    def listen(self):
        
        while True:
            if self.input_flag: #Runs only if no other commands are being sent
                self._event.set() #Sets internal flag to true to block the set_command() function

                
                #All commands sent receive data for 4 channels separated by commas
                '''
                power = self.send_command('get_mpd all', True)
                
                laser_current = self.send_command('get_ld_crnt', True)
                
                pump_current = self.send_command('get_ld_tec', True)
                
                pump_temp = self.send_command('get_tpump', True)

                case_temp = self.send_command('get_tcase', True)
                '''
                

                self._event.clear()     #sets the internal flag to false
                self._event.wait(3)     #waits for 1 second
            pass


if __name__ == "__main__":       
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
