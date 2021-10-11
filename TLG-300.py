import sys
import os 
from PyQt5 import QtWidgets, uic
import paramiko
import threading
import time
import configparser
from PyQt5.QtCore import Qt 




serial = 'serial name'
script = 'python3 TLG-300.py'

cwd = os.path.dirname(os.path.realpath(__file__))
cwd = cwd + '\\TLG-300.ui'

class Ui(QtWidgets.QMainWindow):
    
    def __init__(self):
        
        super(Ui, self).__init__()
        uic.loadUi(cwd, self)
        self.settings_box()
        self.show()

        self.num_channels = 48
        self.prev = 0

        self.hertz.toggled.connect(lambda:self.radiobuttons(self.hertz, 0))
        self.nano_meters.toggled.connect(lambda:self.radiobuttons(self.nano_meters, 1))
        self.grid.toggled.connect(lambda:self.radiobuttons(self.grid, 2))
        self.current_unit = 0
        
        self.diser_box.toggled.connect(self.diser_control)

        self.laser_connection()

        self.config_connection()
        self.ssh_setup() 
        
            
    def laser_connection(self):
        self.laser_1.clicked.connect(lambda:self.laser_button(1))
        self.laser_2.clicked.connect(lambda:self.laser_button(2))
        self.laser_3.clicked.connect(lambda:self.laser_button(3))
        self.laser_4.clicked.connect(lambda:self.laser_button(4))
        self.laser_5.clicked.connect(lambda:self.laser_button(5))
        self.laser_6.clicked.connect(lambda:self.laser_button(6))
        self.laser_7.clicked.connect(lambda:self.laser_button(7))
        self.laser_8.clicked.connect(lambda:self.laser_button(8))
        self.laser_9.clicked.connect(lambda:self.laser_button(9))
        self.laser_10.clicked.connect(lambda:self.laser_button(10))

        self.laser_11.clicked.connect(lambda:self.laser_button(11))
        self.laser_12.clicked.connect(lambda:self.laser_button(12))
        self.laser_13.clicked.connect(lambda:self.laser_button(13))
        self.laser_14.clicked.connect(lambda:self.laser_button(14))
        self.laser_15.clicked.connect(lambda:self.laser_button(15))
        self.laser_16.clicked.connect(lambda:self.laser_button(16))
        self.laser_17.clicked.connect(lambda:self.laser_button(17))
        self.laser_18.clicked.connect(lambda:self.laser_button(18))
        self.laser_19.clicked.connect(lambda:self.laser_button(19))
        self.laser_20.clicked.connect(lambda:self.laser_button(20))

        self.laser_21.clicked.connect(lambda:self.laser_button(21))
        self.laser_22.clicked.connect(lambda:self.laser_button(22))
        self.laser_23.clicked.connect(lambda:self.laser_button(23))
        self.laser_24.clicked.connect(lambda:self.laser_button(24))
        self.laser_25.clicked.connect(lambda:self.laser_button(25))
        self.laser_26.clicked.connect(lambda:self.laser_button(26))
        self.laser_27.clicked.connect(lambda:self.laser_button(27))
        self.laser_28.clicked.connect(lambda:self.laser_button(28))
        self.laser_29.clicked.connect(lambda:self.laser_button(29))
        self.laser_30.clicked.connect(lambda:self.laser_button(30))

        self.laser_31.clicked.connect(lambda:self.laser_button(31))
        self.laser_32.clicked.connect(lambda:self.laser_button(32))
        self.laser_33.clicked.connect(lambda:self.laser_button(33))
        self.laser_34.clicked.connect(lambda:self.laser_button(34))
        self.laser_35.clicked.connect(lambda:self.laser_button(35))
        self.laser_36.clicked.connect(lambda:self.laser_button(36))
        self.laser_37.clicked.connect(lambda:self.laser_button(37))
        self.laser_38.clicked.connect(lambda:self.laser_button(38))
        self.laser_39.clicked.connect(lambda:self.laser_button(39))
        self.laser_40.clicked.connect(lambda:self.laser_button(40))

        self.laser_41.clicked.connect(lambda:self.laser_button(41))
        self.laser_42.clicked.connect(lambda:self.laser_button(42))
        self.laser_43.clicked.connect(lambda:self.laser_button(43))
        self.laser_44.clicked.connect(lambda:self.laser_button(44))
        self.laser_45.clicked.connect(lambda:self.laser_button(45))
        self.laser_46.clicked.connect(lambda:self.laser_button(46))
        self.laser_47.clicked.connect(lambda:self.laser_button(47))
        self.laser_48.clicked.connect(lambda:self.laser_button(48))
        

    def config_connection(self):
        self.config_1.clicked.connect(lambda:self.config_button(1))
        self.config_2.clicked.connect(lambda:self.config_button(2))
        self.config_3.clicked.connect(lambda:self.config_button(3))
        self.config_4.clicked.connect(lambda:self.config_button(4))
        self.config_5.clicked.connect(lambda:self.config_button(5))
        self.config_6.clicked.connect(lambda:self.config_button(6))
        self.config_7.clicked.connect(lambda:self.config_button(7))
        self.config_8.clicked.connect(lambda:self.config_button(8))
        self.config_9.clicked.connect(lambda:self.config_button(9))
        self.config_10.clicked.connect(lambda:self.config_button(10))

        self.config_11.clicked.connect(lambda:self.config_button(11))
        self.config_12.clicked.connect(lambda:self.config_button(12))
        self.config_13.clicked.connect(lambda:self.config_button(13))
        self.config_14.clicked.connect(lambda:self.config_button(14))
        self.config_15.clicked.connect(lambda:self.config_button(15))
        self.config_16.clicked.connect(lambda:self.config_button(16))
        self.config_17.clicked.connect(lambda:self.config_button(17))
        self.config_18.clicked.connect(lambda:self.config_button(18))
        self.config_19.clicked.connect(lambda:self.config_button(19))
        self.config_20.clicked.connect(lambda:self.config_button(20))

        self.config_21.clicked.connect(lambda:self.config_button(21))
        self.config_22.clicked.connect(lambda:self.config_button(22))
        self.config_23.clicked.connect(lambda:self.config_button(23))
        self.config_24.clicked.connect(lambda:self.config_button(24))
        self.config_25.clicked.connect(lambda:self.config_button(25))
        self.config_26.clicked.connect(lambda:self.config_button(26))
        self.config_27.clicked.connect(lambda:self.config_button(27))
        self.config_28.clicked.connect(lambda:self.config_button(28))
        self.config_29.clicked.connect(lambda:self.config_button(29))
        self.config_30.clicked.connect(lambda:self.config_button(30))

        self.config_31.clicked.connect(lambda:self.config_button(31))
        self.config_32.clicked.connect(lambda:self.config_button(32))
        self.config_33.clicked.connect(lambda:self.config_button(33))
        self.config_34.clicked.connect(lambda:self.config_button(34))
        self.config_35.clicked.connect(lambda:self.config_button(35))
        self.config_36.clicked.connect(lambda:self.config_button(36))
        self.config_37.clicked.connect(lambda:self.config_button(37))
        self.config_38.clicked.connect(lambda:self.config_button(38))
        self.config_39.clicked.connect(lambda:self.config_button(39))
        self.config_40.clicked.connect(lambda:self.config_button(40))

        self.config_41.clicked.connect(lambda:self.config_button(41))
        self.config_42.clicked.connect(lambda:self.config_button(42))
        self.config_43.clicked.connect(lambda:self.config_button(43))
        self.config_44.clicked.connect(lambda:self.config_button(44))
        self.config_45.clicked.connect(lambda:self.config_button(45))
        self.config_46.clicked.connect(lambda:self.config_button(46))
        self.config_47.clicked.connect(lambda:self.config_button(47))
        self.config_48.clicked.connect(lambda:self.config_button(48))
        

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


    def closeEvent(self,event):
        result = QtWidgets.QMessageBox.question(self,
                      "Confirm Exit...",
                      "Are you sure you want to exit ?",
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)
        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            event.accept()
            self.ssh.close() 


    def radiobuttons(self,unit, param):
        if unit.isChecked():
            print(unit.text())
            self.current_unit = param
            for channel in range(1,self.num_channels + 1):
                eval(f'self.freq_unit_{channel}').setText(unit.text())
                if param == 0:
                    if self.prev == 1:
                        new_value = 299792.458/eval(f'self.freq_{channel}').value()
                    else:
                        new_value = 191.5+(((19/72)*eval(f'self.freq_{channel}').value())-(19/72))

                    eval(f'self.freq_{channel}').setDecimals(4)
                    eval(f'self.freq_{channel}').setMaximum(196.25)
                    eval(f'self.freq_{channel}').setMinimum(191.5)
                    eval(f'self.freq_{channel}').setValue(192)
                    eval(f'self.freq_{channel}').setSingleStep(0.1)
                    eval(f'self.freq_{channel}').setValue(round(new_value,4))
                    
                    
                elif param == 1:
                    if self.prev == 0:
                        new_value = 299792.458/eval(f'self.freq_{channel}').value() 
                    else:
                        new_value = 1565.5-(((379/180)*eval(f'self.freq_{channel}').value())-(379/180))

                    eval(f'self.freq_{channel}').setDecimals(3)
                    eval(f'self.freq_{channel}').setMaximum(1565.5)
                    eval(f'self.freq_{channel}').setMinimum(1527.6)
                    eval(f'self.freq_{channel}').setValue(1530)
                    eval(f'self.freq_{channel}').setSingleStep(0.5)
                    eval(f'self.freq_{channel}').setValue(round(new_value,3))
                    

                else:
                    if self.prev == 0:
                        new_value = 20-((196.25-eval(f'self.freq_{channel}').value())+(19/72))/(19/72)
                    else:
                        new_value = ((1565.5-eval(f'self.freq_{channel}').value()+(379/180)))/(379/180)

                    eval(f'self.freq_{channel}').setDecimals(0)
                    eval(f'self.freq_{channel}').setMaximum(19)
                    eval(f'self.freq_{channel}').setMinimum(1)
                    eval(f'self.freq_{channel}').setSingleStep(1)
                    eval(f'self.freq_{channel}').setValue(round(new_value))
                    

        self.prev = param


    def diser_control(self):
        if self.diser_box.isChecked():
            for channel in range(1,self.num_channels + 1):
                eval(f'self.diser_on_{channel}').setEnabled(False)
                eval(f'self.diser_off_{channel}').setEnabled(False)
                
        else: 
            for channel in range(1,self.num_channels + 1):
                eval(f'self.diser_on_{channel}').setEnabled(True)
                eval(f'self.diser_off_{channel}').setEnabled(True)


    def laser_button(self, channel):
        self.send_command(f'CH{channel}', True)
        if eval(f'self.laser_{(channel)}').isChecked():
            eval(f'self.laser_{(channel)}').setText('Laser: On')
            eval(f'self.led_{channel}').setStyleSheet('border-color: rgb(0, 0, 0);'
                'border-width: 1px;'       
                'border-style: solid;'
                'border-radius: 15px;'
                'background-color: rgb(55, 255, 55);')
            self.send_command('LE1', True)
            
        else:
            eval(f'self.laser_{(channel)}').setText('Laser: Off')
            eval(f'self.led_{channel}').setStyleSheet('border-color: rgb(0, 0, 0);'
                'border-width: 1px;'       
                'border-style: solid;'
                'border-radius: 15px;'
                'background-color: rgb(255, 55, 55);')
            self.send_command('LE0', True)
            

    def config_button(self, channel):
        freq = eval(f'self.freq_{channel}').value()
        power = eval(f'self.power_{channel}').value()
        offset = eval(f'self.offset_{channel}').value()
        self.send_command(f'CH{channel}', True)

        if self.current_unit == 0:
            self.send_command(f'LF{round(freq,4)}', True)

        elif self.current_unit == 1:
            self.send_command(f'LW{round(freq,3)}', True)

        else:
            self.send_command(f'LG{round(freq)}', True)

        self.send_command(f'LP{power}', True)
        self.send_command(f'FT{offset}', True)

        if self.diser_box.isChecked():
            if self.diser_all_on.isChecked():
                self.send_command('DS0', True)
            else:
                self.send_command('DS1', True)
        elif eval(f'self.diser_on_{channel}').isChecked():
            self.send_command('DS0', True)
        else:
            self.send_command('DS1', True)


    def send_command(self, command, response):
        serial_command = command + '\n'  
        
        self.stdin.write(serial_command)
        self.stdin.flush()

        line1 = str(self.stdout.readline()) #Ignore input line when reading
        if response:
            timeout = time.time() + 3       #Waits 5 seconds for a response then timesout
            while time.time() < timeout:
                line2 = str(self.stdout.readline())
                data = line2.splitlines()[0]
                self.input_flag = 1
                print(data)
                return data

            print('read line faliure')
        self.input_flag = 1
        
        

    def ssh_setup(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect('192.168.0.254', username='pi', password='raspberry', timeout=5)
            
            self.stdin, self.stdout, stderr = self.ssh.exec_command(script, get_pty=True)
            self.send_command(serial, True)
            
            
        except:
            print('Connection failed. \nCheck connection and try again')
            quit()



if __name__ == "__main__":       
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
