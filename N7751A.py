
import sys
import os 
from PyQt5 import QtWidgets, uic
import paramiko
import threading
import time
import configparser


serial = 'USB0::1689::842::C010782::0::INSTR'
script = 'python3 N77.py'

cwd = os.path.dirname(os.path.realpath(__file__))
cwd = cwd + '\\N7751A.ui'

class Ui(QtWidgets.QMainWindow):

    def __init__(self):

        super(Ui, self).__init__()
        uic.loadUi(cwd, self)
        self.show()

        self.input_flag = 0

        #set up ssh connection to raspberry pi
        self.ssh_setup() 
        self.send_command(serial,True)

        #connect buttons to save and open files
        self.actionSave.triggered.connect(self.file_save)
        self.actionOpen.triggered.connect(self.file_open)

        #############
        #initialise inputs to send specific commands to instrument
        self.atten12_setup()
        self.pm5_setup()
        self.pm6_setup()

        
        


        


    def closeEvent(self,event):
        result = QtWidgets.QMessageBox.question(self,
                      "Confirm Exit...",
                      "Are you sure you want to exit ?",
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)
        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            event.accept() 
            self.ssh.close()


    #attenuator inputs
    def atten12_setup(self):
        self.pwr_on.clicked.connect(self.atten_pwr)

        #control subset
        self.alpha_set.valueChanged.connect(lambda:self.send_command('inp1:att ' + str(self.alpha_set.value()) +'db', False))
        self.pwr_set.valueChanged.connect(lambda:self.send_command('outp1:pow ' + str(self.pwr_set.value()) +'dbm', False))
        self.pwr_crtl.currentIndexChanged.connect(lambda:self.send_command('outp1:pow:contr ' + self.pwr_crtl.currentText(), False))
        self.speed.valueChanged.connect(lambda:self.send_command('inp1:att:spe ' + str(self.speed.value()), False))

        #offsets subset
        self.alpha_offset.valueChanged.connect(lambda:self.send_command('inp1:offs ' + str(self.alpha_offset.value()) +'db', False))
        self.pwr_offset.valueChanged.connect(lambda:self.send_command('outp1:pow:offs ' + str(self.pwr_offset.value()) +'db', False))

        #settings subset
        self.A_wavelength.valueChanged.connect(lambda:self.send_command('inp1:wav ' + str(self.A_wavelength.value()) +'nm', False))
        self.A_avg_time.valueChanged.connect(lambda:self.send_command('outp1:atim ' + str(self.A_avg_time.value())+'ms', False))
        self.A_pwr_unit.currentIndexChanged.connect(lambda:self.send_command('outp1:pow:un ' + self.A_pwr_unit.currentText(), False))


    #powermeter channel 5 inputs
    def pm5_setup(self):
        self.P_ref_1.clicked.connect(lambda:self.send_command(f'sens5:pow:ref:disp', False))

        #settings subset
        self.P_wavelength_1.valueChanged.connect(lambda:self.send_command('sens5:pow:wav ' + str(self.P_wavelength_1.value()) +'nm', False))
        self.P_avg_time_1.valueChanged.connect(lambda:self.send_command('sens5:pow:atim ' + str(self.P_avg_time_1.value()) +'ms', False))
        self.P_pwr_unit_1.currentIndexChanged.connect(lambda:self.send_command('sens5:pow:unit ' + self.P_pwr_unit_1.currentText(), False))
        self.pwr_range_1.currentIndexChanged.connect(lambda:self.send_command('sens5:pow:rang ' + self.pwr_range_1.currentText(), False))
        self.range_mode_1.currentIndexChanged.connect(lambda:self.range_mode_func(1))

        #reference subset
        self.ref_mode_1.currentIndexChanged.connect(lambda:self.ref_mode_func(1))
        self.ref_channel_1.valueChanged.connect(lambda:self.send_command('sens5:pow:ref tomod ' + str(self.ref_channel_1.value()) + 'db', False))
        self.ref_val_1.valueChanged.connect(lambda:self.send_command('sens5:pow:ref toref ' + str(self.ref_val_1.value()) + 'dbm', False))
        self.calib_1.valueChanged.connect(lambda:self.send_command('sens5:corr ' + str(self.calib_1.value()) + 'db', False))
    

    
    #powermeter channel 6 inputs
    def pm6_setup(self):
        self.P_ref_2.clicked.connect(lambda:self.send_command(f'sens6:pow:ref:disp', False))

        #settings subset
        self.P_wavelength_2.valueChanged.connect(lambda:self.send_command('sens6:pow:wav ' + str(self.P_wavelength_2.value()) +'nm', False))
        self.P_avg_time_2.valueChanged.connect(lambda:self.send_command('sens6:pow:atim ' + str(self.P_avg_time_2.value()) +'ms', False))
        self.P_pwr_unit_2.currentIndexChanged.connect(lambda:self.send_command('sens6:pow:unit ' + self.P_pwr_unit_2.currentText(), False))
        self.pwr_range_2.currentIndexChanged.connect(lambda:self.send_command('sens6:pow:rang ' + self.pwr_range_2.currentText(), False))
        self.range_mode_2.currentIndexChanged.connect(lambda:self.range_mode_func(2))

        #reference subset
        self.ref_mode_2.currentIndexChanged.connect(lambda:self.ref_mode_func(2))
        self.ref_channel_2.valueChanged.connect(lambda:self.send_command('sens6:pow:ref tomod ' + str(self.ref_channel_2.value()) + 'db', False))
        self.ref_val_2.valueChanged.connect(lambda:self.send_command('sens6:pow:ref toref ' + str(self.ref_val_2.value()) + 'dbm', False))
        self.calib_2.valueChanged.connect(lambda:self.send_command('sens6:corr ' + str(self.calib_2.value()) + 'db', False))


    def atten_pwr(self):
        if self.pwr_on.isChecked():
            self.pwr_on.setStyleSheet('QPushButton'
                '{'
                'border-color: rgb(0, 0, 127);'
                'font: 20pt "MS Shell Dlg 2";'
                'border-width: 2px;'        
                'border-style: solid;'
                'border-radius: 12px;'
                'background-color: rgb(255, 255, 255);'
                '}'
                'QPushButton::hover'
                    '{'
                    'background-color : rgb(215, 240, 255);'
                    '}')

            self.pwr_led.setStyleSheet('border-color: rgb(0, 0, 127);'
                'border-width: 2px;'       
                'border-style: solid;'
                'border-radius: 15px;'
                'background-color: rgb(55, 255, 55);')
            self.send_command('outp1 on', False)

        else:
            self.pwr_on.setStyleSheet('QPushButton'
                '{'
                'border-color: rgb(0, 0, 127);'
                'font: 20pt "MS Shell Dlg 2";'
                'border-width: 2px;'        
                'border-style: solid;'
                'border-radius: 12px;'
                'background-color: rgb(255, 255, 255);'
                '}'
                'QPushButton::hover'
                    '{'
                    'background-color : rgb(215, 240, 255);'
                    '}')
            self.pwr_led.setStyleSheet('border-color: rgb(0, 0, 127);'
                'border-width: 2px;'       
                'border-style: solid;'
                'border-radius: 15px;'
                'background-color: rgb(255, 55, 55);')
            self.send_command('outp1 off', False)
    

    def ref_mode_func(self,channel):
        if eval(f'self.ref_mode_{channel}').currentIndex()==0: 
           eval(f'self.ref_channel_{channel}').setEnabled(False) 
           eval(f'self.ref_val_{channel}').setEnabled(True)
           command = 'sens' + str(channel+4) + ':pow:ref toref ' + str(eval(f'self.ref_val_{channel}').value()) + 'dbm'
           self.send_command(command, False)

        else:
            eval(f'self.ref_channel_{channel}').setEnabled(True)
            eval(f'self.ref_val_{channel}').setEnabled(False)
            command = 'sens' + str(channel+4) + ':pow:ref tomod ' + str(eval(f'self.ref_val_{channel}').value()) + 'db'
            self.send_command(command, False)       
   

    def range_mode_func(self, channel):
        if eval(f'self.range_mode_{channel}').currentIndex()==0:
            mode = '1'
            eval(f'self.pwr_range_{channel}').setEnabled(False)
        else:
            mode = '0'
            eval(f'self.pwr_range_{channel}').setEnabled(True)
        command = 'sens' + str(channel+4) + ':pow:rang:auto ' + mode
        self.send_command(command, False)


    def send_command(self, command, response):
        print(command) 

        visa_command = command + '\n'
        
        self.input_flag = 1
        self.stdin.write(visa_command)
        self.stdin.flush()

        line1 = str(self.stdout.readline()) #ignore input line
        if response:
            time.sleep(.01)
            try:
                line2 = str(self.stdout.readline())
                x = line2.splitlines()[0]
                print(x)
            except:
                print('read line faliure')
        self.input_flag = 0


    def listen(self):
        while True:
            if self.input_flag == 0:
                if self.stdout.channel.recv_ready():
                    line = str(self.stdout.readline())
                    x = line.splitlines()[0]
                    print(x)
            pass


    def ssh_setup(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect('192.168.0.254', username='pi', password='raspberry', timeout=5)
            
            self.stdin, self.stdout, stderr = self.ssh.exec_command(command=script, timeout=3, get_pty=True)

            
            x = threading.Thread(target=self.listen, daemon=True)
            x.start()
        except:
            print('Connection failed. \nCheck connection and try again')
            quit()


    def file_save(self):
        try:
            #Save array as text file
            name = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File')[0]
            if(name[len(name)-4:len(name)] != '.ini'):
                name = name + '.ini'
            with open(name, 'w') as configfile:
                config = configparser.ConfigParser()
                config['atten12'] = {}
                atten12 = config['atten12']

                atten12['alpha_set'] = str(self.alpha_set.value())
                atten12['pwr_set'] = str(self.pwr_set.value())
                atten12['pwr_crtl'] = str(self.pwr_crtl.currentIndex())
                atten12['speed'] = str(self.speed.value())
                
                atten12['alpha_offset'] = str(self.alpha_offset.value())
                atten12['pwr_offset'] = str(self.pwr_offset.value())
                atten12['pwr_n'] = str(self.pwr_n.currentIndex())
                
                atten12['wavelength'] = str(self.A_wavelength.value())
                atten12['avg_time'] = str(self.A_avg_time.value())
                atten12['pwr_unit'] = str(self.A_pwr_unit.currentIndex())

                config['power5'] = {}
                power5 = config['power5']

                power5['wavelength'] = str(self.P_wavelength_1.value())
                power5['avg_time'] = str(self.P_avg_time_1.value())
                power5['pwr_unit'] = str(self.P_pwr_unit_1.currentIndex())
                power5['pwr_range'] = str(self.pwr_range_1.currentIndex())
                power5['range_mode'] = str(self.range_mode_1.currentIndex())

                power5['ref_mode'] = str(self.ref_mode_1.currentIndex())
                power5['ref_channel'] = str(self.ref_channel_1.value())
                power5['ref_val'] = str(self.ref_val_1.value())
                power5['calib'] = str(self.calib_1.value())

                config['power6'] = {}
                power6 = config['power6']

                power6['wavelength'] = str(self.P_wavelength_2.value())
                power6['avg_time'] = str(self.P_avg_time_2.value())
                power6['pwr_unit'] = str(self.P_pwr_unit_2.currentIndex())
                power6['pwr_range'] = str(self.pwr_range_2.currentIndex())
                power6['range_mode'] = str(self.range_mode_2.currentIndex())

                power6['ref_mode'] = str(self.ref_mode_2.currentIndex())
                power6['ref_channel'] = str(self.ref_channel_2.value())
                power6['ref_val'] = str(self.ref_val_2.value())
                power6['calib'] = str(self.calib_2.value())


                config.write(configfile)

        except:
            print('Save failed')
            pass            


    def file_open(self):
        try:
            #Read text file and create array of variables
            ini_path = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File')[0]

            config = configparser.ConfigParser()
            config.read(ini_path)

            #Variables are then set from array. Variable type may need to change
            self.alpha_set.setValue(float(config.get('atten12', 'alpha_set')))
            self.pwr_set.setValue(float(config.get('atten12', 'pwr_set')))
            self.pwr_crtl.setCurrentIndex(int(config.get('atten12', 'pwr_crtl')))
            self.speed.setValue(int(config.get('atten12', 'speed')))

            self.alpha_offset.setValue(float(config.get('atten12', 'alpha_offset')))
            self.pwr_offset.setValue(float(config.get('atten12', 'pwr_offset')))
            self.pwr_n.setCurrentIndex(int(config.get('atten12', 'pwr_n')))

            self.A_wavelength.setValue(int(config.get('atten12', 'wavelength')))
            self.A_avg_time.setValue(int(config.get('atten12', 'avg_time')))
            self.A_pwr_unit.setCurrentIndex(int(config.get('atten12', 'pwr_unit')))
            

            #powermeter channel 5
            self.P_wavelength_1.setValue(int(config.get('power5', 'wavelength')))
            self.P_avg_time_1.setValue(int(config.get('power5', 'avg_time')))
            self.P_pwr_unit_1.setCurrentIndex(int(config.get('power5', 'pwr_unit')))
            self.pwr_range_1.setCurrentIndex(int(config.get('power5', 'pwr_range')))
            self.range_mode_1.setCurrentIndex(int(config.get('power5', 'range_mode')))

            self.ref_mode_1.setCurrentIndex(int(config.get('power5', 'ref_mode')))
            self.ref_channel_1.setValue(float(config.get('power5', 'ref_channel')))
            self.ref_val_1.setValue(float(config.get('power5', 'ref_val')))
            self.calib_1.setValue(float(config.get('power5', 'calib')))

            #powermeter channel 6
            self.P_wavelength_2.setValue(int(config.get('power6', 'wavelength')))
            self.P_avg_time_2.setValue(int(config.get('power6', 'avg_time')))
            self.P_pwr_unit_2.setCurrentIndex(int(config.get('power6', 'pwr_unit')))
            self.pwr_range_2.setCurrentIndex(int(config.get('power6', 'pwr_range')))
            self.range_mode_2.setCurrentIndex(int(config.get('power6', 'range_mode')))

            self.ref_mode_2.setCurrentIndex(int(config.get('power6', 'ref_mode')))
            self.ref_channel_2.setValue(float(config.get('power6', 'ref_channel')))
            self.ref_val_2.setValue(float(config.get('power6', 'ref_val')))
            self.calib_2.setValue(float(config.get('power6', 'calib')))

        
        except:
            print('Open failed')
            pass


if __name__ == "__main__":       
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()

