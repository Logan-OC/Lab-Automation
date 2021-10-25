import sys
import os 
from PyQt5 import QtWidgets, uic
import paramiko
from PyQt5.QtCore import Qt 




serial = 'serial name'          #Enter instrument serial address here
script = 'python3 serial.py'    #This instrument uses serial to communicate

cwd = os.path.dirname(os.path.realpath(__file__))
cwd = cwd + '\\TLG-300.ui'      #UI file directory

class Ui(QtWidgets.QMainWindow):
    
    def __init__(self):
        
        super(Ui, self).__init__()
        uic.loadUi(cwd, self)
        self.settings_box()     #Creates settings box in top right-hand corner
        self.show()

        self.num_channels = 8

        self.prev = 0           #Initialise frequency unit type
        self.current_unit = 0   

        #Connect parameter unit radio buttons in top right-hand corner
        self.hertz.toggled.connect(lambda:self.radiobuttons(self.hertz, 0))
        self.nano_meters.toggled.connect(lambda:self.radiobuttons(self.nano_meters, 1))
        self.grid.toggled.connect(lambda:self.radiobuttons(self.grid, 2))
        
        #Connect diser control buttons in top right-hand corner
        self.diser_box.toggled.connect(self.diser_control)


        self.laser_connection()     #Connects each channel's laser on/off button
        self.config_connection()    #Connects each channel's diser control button

        #Set-up SSH connection
        self.ssh_setup() 

        #The first command sent is the serial address for the device we are connecting to
        self.send_command(serial, True)
        
     

    #Connects every channel's laser on/off button 
    def laser_connection(self):
        self.laser_1.clicked.connect(lambda:self.laser_button(1))
        self.laser_2.clicked.connect(lambda:self.laser_button(2))
        self.laser_3.clicked.connect(lambda:self.laser_button(3))
        self.laser_4.clicked.connect(lambda:self.laser_button(4))
        self.laser_5.clicked.connect(lambda:self.laser_button(5))
        self.laser_6.clicked.connect(lambda:self.laser_button(6))
        self.laser_7.clicked.connect(lambda:self.laser_button(7))
        self.laser_8.clicked.connect(lambda:self.laser_button(8))
          
        
    #Connects every channe;'s configure button
    def config_connection(self):
        self.config_1.clicked.connect(lambda:self.config_button(1))
        self.config_2.clicked.connect(lambda:self.config_button(2))
        self.config_3.clicked.connect(lambda:self.config_button(3))
        self.config_4.clicked.connect(lambda:self.config_button(4))
        self.config_5.clicked.connect(lambda:self.config_button(5))
        self.config_6.clicked.connect(lambda:self.config_button(6))
        self.config_7.clicked.connect(lambda:self.config_button(7))
        self.config_8.clicked.connect(lambda:self.config_button(8))


    #function creates the box in the top-right corner of the GUI
    def settings_box(self):
        # create the container and its layout
        self.settings_container = QtWidgets.QWidget()
        self.settings_container.setGeometry(0,0,50,50)
        settings_layout = QtWidgets.QHBoxLayout(self.settings_container)

        settings_layout.setContentsMargins(2, 2, 2, 2)

        

        self.unit_box = QtWidgets.QGroupBox('Parameter Unit')
        self.diser_box = QtWidgets.QGroupBox('Diser Control All')
        self.diser_box.setCheckable(True)
        self.diser_box.setChecked(False)
        settings_layout.addWidget(self.unit_box)
        settings_layout.addWidget(self.diser_box)

        unit_layout = QtWidgets.QHBoxLayout()
        self.unit_box.setLayout(unit_layout)

        self.hertz = QtWidgets.QRadioButton('THz')
        self.nano_meters = QtWidgets.QRadioButton('nm')
        self.grid = QtWidgets.QRadioButton('GRID')
        unit_layout.addWidget(self.hertz)
        unit_layout.addWidget(self.nano_meters)
        unit_layout.addWidget(self.grid)

        diser_layout = QtWidgets.QHBoxLayout()
        self.diser_box.setLayout(diser_layout)

        self.diser_all_on = QtWidgets.QRadioButton('Diser On')
        self.diser_all_off = QtWidgets.QRadioButton('Diser Off')
        diser_layout.addWidget(self.diser_all_on)
        diser_layout.addWidget(self.diser_all_off)
        
        # set the container as the corner widget; as the docs explain,
        # despite using "TopRightCorner", only the horizontal element (right
        # in this case) will be used 
        self.tabWidget.setCornerWidget(self.settings_container, Qt.TopRightCorner)
        
        self.settings_container.setStyleSheet('font-size: 17pt;')
        unit_layout.setContentsMargins(0,25,0,0)
        diser_layout.setContentsMargins(0,25,0,0)
        self.unit_box.setStyleSheet(
           'QGroupBox{'
            'border-color: rgb(100, 100, 100);'
            'border-width: 1px;'        
            'border-style: solid;'
            'border-radius: 10px;'
            'height: 80px;'
            'padding 10px'
            '}'
            'QGroupBox:title{'
            'padding-top: -5px;'
            'padding-left: -4px;'
            'color: rgb(0, 0, 255);}')
        
        self.diser_box.setStyleSheet(
            'QGroupBox{'
            'border-color: rgb(100, 100, 100);'
            'border-width: 1px;'        
            'border-style: solid;'
            'border-radius: 10px;'
            'height: 80px;'
            '}'
            'QGroupBox:title{'
            'padding-top: -5px;'
            'padding-left: 2px;'
            'color: rgb(0, 0, 255);}')
        
        self.hertz.setChecked(True)
        self.diser_all_off.setChecked(True)


    #Prompts the user bvefore exiting
    def closeEvent(self,event):
        result = QtWidgets.QMessageBox.question(self,
                      "Confirm Exit...",
                      "Are you sure you want to exit ?",
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)
        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            event.accept()
            self.ssh.close()        #Closes the ssh connection to the raspberry pi


    #sets whether hertz, wavelength or GRID is used for laser frequency
    def radiobuttons(self,unit, param):
        if unit.isChecked():
            
            self.current_unit = param       #Stores current unit type for use in config_button function
            for channel in range(1,self.num_channels + 1):      #Changes setting for all channels
                eval(f'self.freq_unit_{channel}').setText(unit.text())

                #Sets the laser frequency in hertz
                if param == 0:
                    if self.prev == 1:
                        new_value = 299792.458/eval(f'self.freq_{channel}').value()         #Converts wavelength to hertz
                    else:
                        new_value = 191.5+(((19/72)*eval(f'self.freq_{channel}').value())-(19/72))      #Converts GRID to hertz

                    eval(f'self.freq_{channel}').setDecimals(4)
                    eval(f'self.freq_{channel}').setMaximum(196.25)
                    eval(f'self.freq_{channel}').setMinimum(191.5)
                    eval(f'self.freq_{channel}').setValue(192)
                    eval(f'self.freq_{channel}').setSingleStep(0.1)
                    eval(f'self.freq_{channel}').setValue(round(new_value,4))
                    
                #Sets the laser frequency in terms of wavelength    
                elif param == 1:
                    if self.prev == 0:
                        new_value = 299792.458/eval(f'self.freq_{channel}').value()         #Converts hertz to wavelength
                    else:
                        new_value = 1565.5-(((379/180)*eval(f'self.freq_{channel}').value())-(379/180))     #Converts GRID to wavelength

                    eval(f'self.freq_{channel}').setDecimals(3)
                    eval(f'self.freq_{channel}').setMaximum(1565.5)
                    eval(f'self.freq_{channel}').setMinimum(1527.6)
                    eval(f'self.freq_{channel}').setValue(1530)
                    eval(f'self.freq_{channel}').setSingleStep(0.5)
                    eval(f'self.freq_{channel}').setValue(round(new_value,3))
                    
                #Sets the laser frequency in terms of GRID value
                else:
                    if self.prev == 0:
                        new_value = 20-((196.25-eval(f'self.freq_{channel}').value())+(19/72))/(19/72)      #Converts hertz to GRID
                    else:
                        new_value = ((1565.5-eval(f'self.freq_{channel}').value()+(379/180)))/(379/180)     #Converts wavelength to GRID

                    eval(f'self.freq_{channel}').setDecimals(0)
                    eval(f'self.freq_{channel}').setMaximum(19)
                    eval(f'self.freq_{channel}').setMinimum(1)
                    eval(f'self.freq_{channel}').setSingleStep(1)
                    eval(f'self.freq_{channel}').setValue(round(new_value))
                    
        #Stores current unit type as previous for conversion if changed
        self.prev = param


    #Enables or diables every channel's diser control settings depending on overall diser control in top RHC
    def diser_control(self):
        if self.diser_box.isChecked():
            for channel in range(1,self.num_channels + 1):
                eval(f'self.diser_on_{channel}').setEnabled(False)
                eval(f'self.diser_off_{channel}').setEnabled(False)
                
        else: 
            for channel in range(1,self.num_channels + 1):
                eval(f'self.diser_on_{channel}').setEnabled(True)
                eval(f'self.diser_off_{channel}').setEnabled(True)


    #Sends command to enable laser
    def laser_button(self, channel):
        self.send_command(f'CH{channel}', True)     #Sets the current channel to control

        if eval(f'self.laser_{(channel)}').isChecked():
            eval(f'self.laser_{(channel)}').setText('Laser: On')

            #Changes LED to green
            eval(f'self.led_{channel}').setStyleSheet('border-color: rgb(0, 0, 0);'
                'border-width: 1px;'       
                'border-style: solid;'
                'border-radius: 15px;'
                'background-color: rgb(55, 255, 55);')

            self.send_command('LE1', True)          #Turns laser on
            
        else:
            eval(f'self.laser_{(channel)}').setText('Laser: Off')

            #Changes LED to green
            eval(f'self.led_{channel}').setStyleSheet('border-color: rgb(0, 0, 0);'
                'border-width: 1px;'       
                'border-style: solid;'
                'border-radius: 15px;'
                'background-color: rgb(255, 55, 55);')
            self.send_command('LE0', True)          #Turns laser off
            

    def config_button(self, channel):
        freq = eval(f'self.freq_{channel}').value()
        power = eval(f'self.power_{channel}').value()
        offset = eval(f'self.offset_{channel}').value()

        self.send_command(f'CH{channel}', True) #Sets the current channel to control

        #Checks channelfrequency unit type and sends corresponding command
        if self.current_unit == 0:
            self.send_command(f'LF{round(freq,4)}', True)
        elif self.current_unit == 1:
            self.send_command(f'LW{round(freq,3)}', True)
        else:
            self.send_command(f'LG{round(freq)}', True)

        #Sends commands for power and offset
        self.send_command(f'LP{power}', True)
        self.send_command(f'FT{offset}', True)

        #Checks total diser control status, if not, checks channell diser control status
        #Sends diser on/off command 
        if self.diser_box.isChecked():
            if self.diser_all_on.isChecked():
                self.send_command('DS0', True)
            else:
                self.send_command('DS1', True)

        elif eval(f'self.diser_on_{channel}').isChecked():
            self.send_command('DS0', True)
        else:
            self.send_command('DS1', True)


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
            print(data)
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



if __name__ == "__main__":       
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
