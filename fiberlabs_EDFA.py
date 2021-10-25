import sys
import os 
from PyQt5 import QtWidgets, uic
import paramiko
import threading
from PyQt5.QtCore import Qt 
import numpy as np




serial = 'serial name'          #Enter instrument serial address here
script = 'python3 serial.py'    #This instrument uses serial to communicate

cwd = os.path.dirname(os.path.realpath(__file__))
cwd = cwd + '\\fiberlabs_EDFA.ui'   #UI file directory

class Ui(QtWidgets.QMainWindow):
    
    def __init__(self):
        
        super(Ui, self).__init__()
        uic.loadUi(cwd, self)
        self.settings_box()
        self.show()

        #Flag to prevent threads accessing the send_command() function at the same time
        self.input_flag = 0

        self.num_channels = 4

        #A list used to determine which driving mode is lected for each pump
        #ALC is set by default
        self.driving_mode = [0,0,0,0]

        #Lists containing the values for each channel
        self.power_in = ['N/A','N/A','N/A','N/A']
        self.power_out = ['N/A','N/A','N/A','N/A']
        self.current = ['N/A','N/A','N/A','N/A']
        self.temp = ['N/A','N/A','N/A','N/A']

        #Intialise arrays containing the values for each alarm channel
        # alm_n_val[4][0] is used to store the index of the last channel accessed and index[4][1] and [4][2] are not used
        self.alm_1_val = np.array([[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]])
        self.alm_2_val = np.array([[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]])
        self.alm_3_val = np.array([[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]])
        self.alm_4_val = np.array([[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]])
        self.alm_5_val = np.array([[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]])
        self.alm_6_val = np.array([[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]])


        #Saves the current settings to EEPROM
        self.actionSave.triggered.connect(lambda:self.send_command('saveref', True))

        #Connect the button to power the amplifier
        self.amp_button.clicked.connect(self.amp_led_func)

        #Connect the radio buttons for each pumps driving mode
        self.ACC_1.toggled.connect(lambda:self.radiobuttons(1))
        self.ALC_1.toggled.connect(lambda:self.radiobuttons(1))
        self.ACC_2.toggled.connect(lambda:self.radiobuttons(2))
        self.ALC_2.toggled.connect(lambda:self.radiobuttons(2))
        self.ACC_3.toggled.connect(lambda:self.radiobuttons(3))
        self.ALC_3.toggled.connect(lambda:self.radiobuttons(3))
        self.ACC_4.toggled.connect(lambda:self.radiobuttons(4))
        self.ALC_4.toggled.connect(lambda:self.radiobuttons(4))

        #Connects the spinbox to send a command when a value is changed
        self.set_value_1.valueChanged.connect(lambda:self.set_mode_val(1))
        self.set_value_2.valueChanged.connect(lambda:self.set_mode_val(2)) 
        self.set_value_3.valueChanged.connect(lambda:self.set_mode_val(3))
        self.set_value_4.valueChanged.connect(lambda:self.set_mode_val(4))
        

        #Connect the 'set alarm' buttons with the appropriate command string
        self.alm_set_1.clicked.connect(lambda:self.alm_set(1, 'almout'))
        self.alm_set_2.clicked.connect(lambda:self.alm_set(2, 'almin'))
        self.alm_set_3.clicked.connect(lambda:self.alm_set(3, 'almret'))
        self.alm_set_4.clicked.connect(lambda:self.alm_set(4, 'almctmp'))
        self.alm_set_5.clicked.connect(lambda:self.alm_set(5, 'almldc'))
        self.alm_set_6.clicked.connect(lambda:self.alm_set(6, 'almldt'))

        #Stores and retrieves the alarms values from self.alm_n_val
        self.alm_1.currentIndexChanged.connect(lambda:self.alm_channel(1))
        self.alm_2.currentIndexChanged.connect(lambda:self.alm_channel(2))
        self.alm_3.currentIndexChanged.connect(lambda:self.alm_channel(3))
        self.alm_4.currentIndexChanged.connect(lambda:self.alm_channel(4))
        self.alm_5.currentIndexChanged.connect(lambda:self.alm_channel(5))
        self.alm_6.currentIndexChanged.connect(lambda:self.alm_channel(6))
        
        #Set-up SSH connection
        self.ssh_setup() 
        #The first command sent is the serial address for the device we are connecting to
        self.send_command(serial, True)

        #Initialisation for multithreading
        self._event = threading.Event()
        self._thread = threading.Thread(target=self.listen, daemon=True)
        self._thread.start()
        


    
    #function creates the power enable box in the top-right corner of the GUI
    def settings_box(self):
        # create the container and its layout
        self.settings_container = QtWidgets.QWidget()
        self.settings_container.setGeometry(0,0,50,50)
        settings_layout = QtWidgets.QHBoxLayout(self.settings_container)

        settings_layout.setContentsMargins(2, 2, 20, 2)

        #Create a box to place the widgets
        self.amp_box = QtWidgets.QGroupBox()
        settings_layout.addWidget(self.amp_box)

        amp_layout = QtWidgets.QHBoxLayout()
        self.amp_box.setLayout(amp_layout)

        #Add the widgets to the box
        self.amp_button = QtWidgets.QPushButton('Power')
        self.amp_led = QtWidgets.QLabel()
        amp_layout.addWidget(self.amp_button)
        amp_layout.addWidget(self.amp_led)
        self.amp_button.setCheckable(True)

        
        # set the container as the corner widget
        self.tabWidget.setCornerWidget(self.settings_container, Qt.TopRightCorner)
        
        #Set all stylesheets for the container
        self.settings_container.setStyleSheet('font-size: 17pt;')
        
        self.amp_box.setStyleSheet(
           'QGroupBox{'
            'border-color: rgb(100, 100, 100);'
            'border-width: 1px;'        
            'border-style: solid;'
            'border-radius: 10px;'
            'height: 80px;'
            'width: 200px;'
            'padding-right 30px'
            '}')
        self.amp_button.setStyleSheet(
            'QPushButton{'
            'border-color: rgb(100, 100, 100);'
            'font: 20pt "MS Shell Dlg 2";'
            'border-width: 2px;'        
            'border-style: outset;'
            'border-radius: 8px;'
            'background-color: rgb(255, 255, 255);'
            'padding-right 20px'
            '}'
            'QPushButton:hover{'
            'background-color: rgb(225, 240, 255);'
            '}'
            'QPushButton:pressed{'
            'background-color: rgb(245, 245, 245);'
            '}')

        self.amp_led.setFixedSize(30, 30)
        
        self.amp_led.setStyleSheet(
            'border-color: rgb(0, 0, 0);'
            'border-width: 1px;'        
            'border-style: solid;'
            'border-radius: 15px;'
            'background-color: rgb(255, 55, 55);')
        

    #Prompts the user bvefore exiting
    def closeEvent(self,event):
        result = QtWidgets.QMessageBox.question(self,
                      "Confirm Exit...",
                      "Are you sure you want to exit ?",
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)
        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            event.accept()
            self.ssh.close()    #Closes the ssh connection to the raspberry pi


    #Displays 'set current' or 'set power' for whichever driving mode is selected
    def radiobuttons(self, channel ):
        if eval(f'self.ACC_{channel}').isChecked():
            
            eval(f'self.set_label_{channel}').setText('Set Current')
            eval(f'self.set_unit_{channel}').setText('mA')
            eval(f'self.set_value_{channel}').setDecimals(0)
            eval(f'self.set_value_{channel}').setMaximum(100)
            eval(f'self.set_value_{channel}').setMinimum(0)
            eval(f'self.set_value_{channel}').setValue(0)
            eval(f'self.set_value_{channel}').setSingleStep(10)

            self.driving_mode[channel-1] = 1

        else:
            eval(f'self.set_label_{channel}').setText('Set Power')
            eval(f'self.set_unit_{channel}').setText('dBm')
            eval(f'self.set_value_{channel}').setDecimals(1)
            eval(f'self.set_value_{channel}').setMaximum(30)
            eval(f'self.set_value_{channel}').setMinimum(0)
            eval(f'self.set_value_{channel}').setValue(0)
            eval(f'self.set_value_{channel}').setSingleStep(1)
            self.driving_mode[channel-1] = 0


    #Truns the amplifier on and off
    #Alse turns the LED green
    def amp_led_func(self):
        if self.amp_button.isChecked():
            self.set_command('active,1', True)
            self.amp_led.setStyleSheet('border-color: rgb(0, 0, 0);'
                'border-width: 1px;'       
                'border-style: solid;'
                'border-radius: 15px;'
                'background-color: rgb(55, 255, 55);')
            
        else:
            self.set_command('active,0', True)
            self.amp_led.setStyleSheet('border-color: rgb(0, 0, 0);'
                'border-width: 1px;'       
                'border-style: solid;'
                'border-radius: 15px;'
                'background-color: rgb(255, 55, 55);')


    #Determines the channel's driving mode, then sends the appropriate command to the EDFA
    def set_mode_val(self,channel):
        if self.driving_mode[channel-1]:
            command = f'setacc_{channel},'+ str(eval(f'self.set_value_{channel}').value())
            self.set_command(command, True)
        else:
            command = f'setalc_{channel},'+ str(eval(f'self.set_value_{channel}').value())
            self.set_command(command, True)


    #Sets each alarm
    def alm_set(self, alm, command):
        
        channel = eval(f'self.alm_{alm}').currentIndex() + 1
        thresh =  eval(f'self.alm_th_{alm}').value()
        hyst = eval(f'self.alm_hys_{alm}').value()
        
        if eval(f'self.alm_set_{alm}').isChecked():
            eval(f'self.alm_set_{alm}').setText('On')
            command = (f'{command},{channel},{thresh},1,{hyst}')
            self.set_command(command, True)
        else:
            eval(f'self.alm_set_{alm}').setText('Off')
            command = (f'{command},{channel},{thresh},0,{hyst}')
            self.set_command(command, True)


    #Stores the alarm values and retreives the new values
    def alm_channel(self, alm):
        prev_index = eval(f'self.alm_{alm}_val')[4][0]
        new_index = eval(f'self.alm_{alm}').currentIndex()
        eval(f'self.alm_{alm}_val')[4][0] = new_index
        eval(f'self.alm_{alm}_val')[prev_index][0] = eval(f'self.alm_th_{alm}').value()
        eval(f'self.alm_{alm}_val')[prev_index][1] = eval(f'self.alm_hys_{alm}').value()
        if eval(f'self.alm_set_{alm}').isChecked():
            eval(f'self.alm_{alm}_val')[prev_index][2] = 1
        else:
            eval(f'self.alm_{alm}_val')[prev_index][2] = 0

        new_thresh = eval(f'self.alm_{alm}_val')[new_index][0]
        new_hyst = eval(f'self.alm_{alm}_val')[new_index][1]
        new_set = eval(f'self.alm_{alm}_val')[new_index][2]

        eval(f'self.alm_th_{alm}').setValue(new_thresh)
        eval(f'self.alm_hys_{alm}').setValue(new_hyst)
        if new_set:
            eval(f'self.alm_set_{alm}').setChecked(True)
            eval(f'self.alm_set_{alm}').setText('On')
        else:
            eval(f'self.alm_set_{alm}').setChecked(False)
            eval(f'self.alm_set_{alm}').setText('Off')


    #send the command to be sent, but first ensure the listening thread is complete
    def set_command(self, command, response):
        while True:
            if not self._event.is_set():
                self.input_flag = 0         #blocks the listening thread from running while sending a command
                data = self.send_command(command,response)
                print(data)
                return data
        

    #Sends a command over serial
    #If the command receives a response it is returned
    def send_command(self, command, response):
        serial_command = command + '\n'  
        
        self.stdin.write(serial_command)
        self.stdin.flush()

        line1 = str(self.stdout.readline()) #Ignore input line when reading
        if response:
            line2 = str(self.stdout.readline())
            data = line2.splitlines()[0]
            self.input_flag = 1
            return data

        self.input_flag = 1
                
                
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
            if self.input_flag: #Runs only if no other commands are being sent
                self._event.set() #Sets internal flag to true to block the set_command() function

                #All commands sent receive data for 4 channels separated by commas
                power_in = self.send_command('monin', True)
                self.power_in = power_in.split(',')
                power_out = self.send_command('monout', True)
                self.power_out = power_out.split(',')
                current = self.send_command('monldc', True)
                self.current = current.split(',')
                temp = self.send_command('monldt', True)
                self.temp = temp.split(',')
                
                #Update monitor values
                for channel in range(1,5):
                    try:
                        eval(f'self.power_in_{channel}').setText(str(float(self.power_in[channel-1])))      #Converts string to float to ensure that the value returned is a number
                        eval(f'self.power_out_{channel}').setText(str(float(self.power_out[channel-1])))    #Then converts back to string for writing 
                        eval(f'self.current_{channel}').setText(str(float(self.current[channel-1])))
                        eval(f'self.temp_{channel}').setText(str(float(self.temp[channel-1])))

                    #Otherwise the channel is N/A    
                    except:
                        eval(f'self.power_in_{channel}').setText('N/A')
                        eval(f'self.power_out_{channel}').setText('N/A')
                        eval(f'self.current_{channel}').setText('N/A')
                        eval(f'self.temp_{channel}').setText('N/A')

                self._event.clear()     #sets the internal flag to false
                self._event.wait(2)     #waits for 2 seconds
            pass


if __name__ == "__main__":       
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
