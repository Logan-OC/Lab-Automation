import sys
import os 
from PyQt5 import QtWidgets, uic
import paramiko
import threading
import re



serial = 'serial name'          #Enter instrument serial address here
script = 'python3 serial.py'    #This instrument uses serial to communicat

cwd = os.path.dirname(os.path.realpath(__file__))
cwd = cwd + '\\lightwaves2020_EDFA.ui'  #UI file directory

class Ui(QtWidgets.QMainWindow):
    
    def __init__(self):
        
        super(Ui, self).__init__()
        uic.loadUi(cwd, self)
        self.show()

        #Flag to prevent threads accessing the send_command() function at the same time
        self.thread_flag = 0

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
        
        if alm == 0:        #LOS alarm
            if self.LOS_alm_set.isChecked():
                self.LOS_alm_set.setText('On')
                command = 'set_los ' + str(self.LOS_alm_val.value())
            else:
                self.LOS_alm_set.setText('Off')
                command = 'set_los d'
            self.set_command(command, True)
            
        elif alm == 1:      #Laser current alarm
            if self.current_alm_set.isChecked():
                self.current_alm_set.setText('On')
                command = 'set_alarm_ld_crnt ' + str(self.current_alm_val.value())
            else:
                self.current_alm_set.setText('Off')
                command = 'set_alarm_ld_crnt d'
            self.set_command(command, True)

        else:               #Pump tempurature alarm
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
                self.thread_flag = 0         #blocks the listening thread from running while sending a command
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
            line2 = str(self.stdout.readline())
            data = line2.splitlines()[0]
            self.thread_flag = 1
            print(data)
            return data

        self.thread_flag = 1
                
                
    #Establishes connection to raspberry pi
    #Ensure that the raspberry ip, username and password are correct
    def ssh_setup(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect('192.168.0.254', username='pi', password='raspberry', timeout=5)
            
            self.stdin, self.stdout, stderr = self.ssh.exec_command(command=script, timeout=3, get_pty=True)
                        
        except:
            print('Connection failed. \nCheck connection and try again')
            quit()


    #A seperate thread that continously requests the EDFA monitor values
    def listen(self):
        
        while True:
            if self.thread_flag: #Runs only if no other commands are being sent
                self._event.set() #Sets internal flag to true to block the set_command() function

                
                #Command sent sometimes start with 'msa::edfa>' then some float
                #Uses re.findall to find 1 decimal floats in string
                try:

                    power = self.send_command('get_mpd all', True)
                    power_float_list = re.findall('\d+\.\d+',power)
                    power = power_float_list[0]

                    laser_current = self.send_command('get_ld_crnt', True)
                    Lcurrent_float_list = re.findall('\d+\.\d+',laser_current)
                    laser_current = Lcurrent_float_list[0]
                    
                    pump_current = self.send_command('get_ld_tec', True)
                    Pcurrent_float_list = re.findall('\d+\.\d+',pump_current)
                    pump_current = Pcurrent_float_list[0]
                    
                    pump_temp = self.send_command('get_tpump', True)
                    Ptemp_float_list = re.findall('\d+\.\d+',pump_temp)
                    pump_temp = Ptemp_float_list[0]

                    case_temp = self.send_command('get_tcase', True)
                    Ctemp_float_list = re.findall('\d+\.\d+',case_temp)
                    case_temp = Ctemp_float_list[0]
                    
                
                    self.pwr_out.setText(power)
                    self.laser_current.setText(laser_current)
                    self.pump_current.setText(pump_current)
                    self.pump_temp.setText(pump_temp)
                    self.case_temp.setText(case_temp)

                #If there is an error sets outputs to N/A
                except:
                    self.pwr_out.setText('N/A')
                    self.laser_current.setText('N/A')
                    self.pump_current.setText('N/A')
                    self.pump_temp.setText('N/A')
                    self.case_temp.setText('N/A')
                

                self._event.clear()     #sets the internal flag to false
                self._event.wait(2)     #waits for 2 seconds
            pass


if __name__ == "__main__":       
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()