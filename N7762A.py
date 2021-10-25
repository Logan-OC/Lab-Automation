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
cwd = cwd + '\\N7762A.ui'

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
        self.atten34_setup()



    def closeEvent(self,event):
        result = QtWidgets.QMessageBox.question(self,
                      "Confirm Exit...",
                      "Are you sure you want to exit ?",
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)
        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            event.accept() 
            self.ssh.close()


    #attenuator inputs, channels 3-4
    def atten12_setup(self):
        self.pwr_on_1.clicked.connect(lambda:self.atten_pwr(1))

        #control subset
        self.alpha_set_1.valueChanged.connect(lambda:self.send_command('inp1:att ' + str(self.alpha_set_1.value()) +'db', False))
        self.pwr_set_1.valueChanged.connect(lambda:self.send_command('outp1:pow ' + str(self.pwr_set_1.value()) +'dbm', False))
        self.pwr_crtl_1.currentIndexChanged.connect(lambda:self.send_command('outp1:pow:contr ' + self.pwr_crtl_1.currentText(), False))
        self.speed_1.valueChanged.connect(lambda:self.send_command('inp1:att:spe ' + str(self.speed_1.value()), False))

        #offsets subset
        self.alpha_offset_1.valueChanged.connect(lambda:self.send_command('inp1:offs ' + str(self.alpha_offset_1.value()) +'db', False))
        self.pwr_offset_1.valueChanged.connect(lambda:self.send_command('outp1:pow:offs ' + str(self.pwr_offset_1.value()) +'db', False))

        #settings subset
        self.A_wavelength_1.valueChanged.connect(lambda:self.send_command('inp1:wav ' + str(self.A_wavelength_1.value()) +'nm', False))
        self.A_avg_time_1.valueChanged.connect(lambda:self.send_command('outp1:atim ' + str(self.A_avg_time_1.value())+'ms', False))
        self.A_pwr_unit_1.currentIndexChanged.connect(lambda:self.send_command('outp1:pow:un ' + self.A_pwr_unit_1.currentText(), False))


    #attenuator inputs, channels 3-4
    def atten34_setup(self):
        self.pwr_on_2.clicked.connect(lambda:self.atten_pwr(3))

        #control subset
        self.alpha_set_2.valueChanged.connect(lambda:self.send_command('inp3:att ' + str(self.alpha_set_2.value()) +'db', False))
        self.pwr_set_2.valueChanged.connect(lambda:self.send_command('outp3:pow ' + str(self.pwr_set_2.value()) +'dbm', False))
        self.pwr_crtl_2.currentIndexChanged.connect(lambda:self.send_command('outp3:pow:contr ' + self.pwr_crtl_2.currentText(), False))
        self.speed_2.valueChanged.connect(lambda:self.send_command('inp3:att:spe ' + str(self.speed_2.value()), False))

        #offsets subset
        self.alpha_offset_2.valueChanged.connect(lambda:self.send_command('inp3:offs ' + str(self.alpha_offset_2.value()) +'db', False))
        self.pwr_offset_2.valueChanged.connect(lambda:self.send_command('outp3:pow:offs ' + str(self.pwr_offset_2.value()) +'db', False))

        #settings subset
        self.A_wavelength_2.valueChanged.connect(lambda:self.send_command('inp3:wav ' + str(self.A_wavelength_2.value()) +'nm', False))
        self.A_avg_time_2.valueChanged.connect(lambda:self.send_command('outp3:atim ' + str(self.A_avg_time_2.value())+'ms', False))
        self.A_pwr_unit_2.currentIndexChanged.connect(lambda:self.send_command('outp3:pow:un ' + self.A_pwr_unit_2.currentText(), False))



    def atten_pwr(self, channel):
        if channel==1:
            tab = 1
        else:
            tab = 2
        if eval(f'self.pwr_on_{tab}').isChecked():
            eval(f'self.pwr_on_{tab}').setStyleSheet('QPushButton'
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

            eval(f'self.pwr_led_{tab}').setStyleSheet('border-color: rgb(0, 0, 127);'
                'border-width: 2px;'       
                'border-style: solid;'
                'border-radius: 15px;'
                'background-color: rgb(55, 255, 55);')
            self.send_command(f'outp{channel} on', False)

        else:
            eval(f'self.pwr_on_{tab}').setStyleSheet('QPushButton'
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
            eval(f'self.pwr_led_{tab}').setStyleSheet('border-color: rgb(0, 0, 127);'
                'border-width: 2px;'       
                'border-style: solid;'
                'border-radius: 15px;'
                'background-color: rgb(255, 55, 55);')
            self.send_command(f'outp{channel} off', False)
    
   


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

                atten12['alpha_set'] = str(self.alpha_set_1.value())
                atten12['pwr_set'] = str(self.pwr_set_1.value())
                atten12['pwr_crtl'] = str(self.pwr_crtl_1.currentIndex())
                atten12['speed'] = str(self.speed_1.value())
                
                atten12['alpha_offset'] = str(self.alpha_offset_1.value())
                atten12['pwr_offset'] = str(self.pwr_offset_1.value())
                atten12['pwr_n'] = str(self.pwr_n_1.currentIndex())
                
                atten12['wavelength'] = str(self.A_wavelength_1.value())
                atten12['avg_time'] = str(self.A_avg_time_1.value())
                atten12['pwr_unit'] = str(self.A_pwr_unit_1.currentIndex())
                

                config['atten34'] = {}
                atten34 = config['atten34']

                atten34['alpha_set'] = str(self.alpha_set_2.value())
                atten34['pwr_set'] = str(self.pwr_set_2.value())
                atten34['pwr_crtl'] = str(self.pwr_crtl_2.currentIndex())
                atten34['speed'] = str(self.speed_2.value())
                
                atten34['alpha_offset'] = str(self.alpha_offset_2.value())
                atten34['pwr_offset'] = str(self.pwr_offset_2.value())
                atten34['pwr_n'] = str(self.pwr_n_2.currentIndex())
                
                atten34['wavelength'] = str(self.A_wavelength_2.value())
                atten34['avg_time'] = str(self.A_avg_time_2.value())
                atten34['pwr_unit'] = str(self.A_pwr_unit_2.currentIndex())
                


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
            #attenuator channel 1-2
            self.alpha_set_1.setValue(float(config.get('atten12', 'alpha_set')))
            self.pwr_set_1.setValue(float(config.get('atten12', 'pwr_set')))
            self.pwr_crtl_1.setCurrentIndex(int(config.get('atten12', 'pwr_crtl')))
            self.speed_1.setValue(int(config.get('atten12', 'speed')))

            self.alpha_offset_1.setValue(float(config.get('atten12', 'alpha_offset')))
            self.pwr_offset_1.setValue(float(config.get('atten12', 'pwr_offset')))
            self.pwr_n_1.setCurrentIndex(int(config.get('atten12', 'pwr_n')))

            self.A_wavelength_1.setValue(int(config.get('atten12', 'wavelength')))
            self.A_avg_time_1.setValue(int(config.get('atten12', 'avg_time')))
            self.A_pwr_unit_1.setCurrentIndex(int(config.get('atten12', 'pwr_unit')))


            #attenuator channel 3-4
            self.alpha_set_2.setValue(float(config.get('atten34', 'alpha_set')))
            self.pwr_set_2.setValue(float(config.get('atten34', 'pwr_set')))
            self.pwr_crtl_2.setCurrentIndex(int(config.get('atten34', 'pwr_crtl')))
            self.speed_2.setValue(int(config.get('atten34', 'speed')))

            self.alpha_offset_2.setValue(float(config.get('atten34', 'alpha_offset')))
            self.pwr_offset_2.setValue(float(config.get('atten34', 'pwr_offset')))
            self.pwr_n_2.setCurrentIndex(int(config.get('atten34', 'pwr_n')))

            self.A_wavelength_2.setValue(int(config.get('atten34', 'wavelength')))
            self.A_avg_time_2.setValue(int(config.get('atten34', 'avg_time')))
            self.A_pwr_unit_2.setCurrentIndex(int(config.get('atten34', 'pwr_unit')))
            
        
        except:
            print('Open failed')
            pass


if __name__ == "__main__":       
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()

