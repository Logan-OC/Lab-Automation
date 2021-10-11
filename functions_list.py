from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import paramiko
import configparser

#All functions should be placed within the Ui_MainWindow class unless stated otherwise


#####################################################################################################################
#Establishes connection to raspberry pi
#Ensure that the raspberry ip, username and password are correct
def ssh_setup(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect('192.168.0.254', username='pi', password='raspberry', timeout=5)
        except:
            print('Connection failed. \nCheck connection and try again')
            quit()

#Place this in setupUi to call function
self.ssh_setup()



#####################################################################################################################
#Used to ask if user is sure they want to close window
class MyWindow(QtWidgets.QMainWindow):
    def closeEvent(self,event):
        result = QtWidgets.QMessageBox.question(self,
                      "Confirm Exit...",
                      "Are you sure you want to exit ?",
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)
        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            event.accept() 
#Include this in main    
MainWindow = MyWindow() 


#####################################################################################################################
#Example of what to do when clicking a button
#The command line for the raspberry pi is created and passed off to send_command()
def button_clicked(self, but):
    visa_command1 = '\'SOURCE1:FUNCTION SIN\''
    visa_command2 = '\'SOURCE1:FREQUENCY 15E3\''
    visa_command3 = '\'SOURCE1:VOLTAGE:AMPLITUDE 1.5\''
    script = 'python3 test.py '+ serial + ' '
    print('\n Button '+but+' Clicked \n')
    self.send_command(script + visa_command1)
    self.send_command(script + visa_command2)
    self.send_command(script + visa_command3)
#Serial is the serial number for the instrument you wish to connect
#Can be made as a global variable
serial = 'Serial number for specific instrument'



#Sends a command to the cmd of the raspberry pi ssh session
#Waits for response before continuing
def send_command(self, command):
    stdin, stdout, stderr = self.ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()     #Blocking command, waits for response
    if exit_status == 0:
        pass
    else:
        print("Error", exit_status)
    
    print(f'STDOUT: {stdout.read().decode("utf8")}')
    print(f'STDERR: {stderr.read().decode("utf8")}')
    stdin.close()
    stdout.close()
    stderr.close()


#####################################################################################################################
#Saves the current instrument settings as a text file
def file_save(self):
    try:
        #Save array as text file
        name = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File')[0]
        if(name[len(name)-4:len(name)] != '.ini'):
            name = name + '.ini'
        with open(name, 'w') as configfile:
            config = configparser.ConfigParser()
            config['Data'] = {}
            Data = config['Data']
            Data['Number'] = str(self.input1.value())
            Data['Text'] = str(self.input2.text())

            config.write(configfile)

    except:
        pass


#Opens a text file in a chosen directory
def file_open(self):
        try:
            #Read text file and create array of variables
            ini_path = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File')[0]

            config = configparser.ConfigParser()
            config.read(ini_path)
            Number = config.get('Data', 'Number')
            Text = config.get('Data', 'Text')

            #Variables are then set from array. Variable type may need to change
            self.input1.setValue(float(Number))
            self.input2.setText(Text)
        
        except:
            pass

#For saving and opening files only
#####################################################################################################################
#If not already inside these functions
#Add each line within its specific function

def setupUi(self, MainWindow):      #Function should already exist
    self.actionOpen = QtWidgets.QAction(MainWindow)
    self.actionOpen.setShortcutVisibleInContextMenu(True)
    self.actionOpen.setObjectName("actionOpen")
    self.actionOpen.triggered.connect(self.file_open)


    self.actionSave = QtWidgets.QAction(MainWindow)
    self.actionSave.setShortcutVisibleInContextMenu(True)
    self.actionSave.setObjectName("actionSave")
    self.actionSave.triggered.connect(self.file_save)

    self.menuFile.addAction(self.actionOpen)
    self.menuFile.addAction(self.actionSave)
    self.menubar.addAction(self.menuFile.menuAction())

    self.retranslateUi(MainWindow)
    QtCore.QMetaObject.connectSlotsByName(MainWindow)

def retranslateUi(self, MainWindow):      #Function should already exist
    _translate = QtCore.QCoreApplication.translate
    MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

    self.menuFile.setTitle(_translate("MainWindow", "File"))
    self.actionOpen.setText(_translate("MainWindow", "Open"))
    self.actionOpen.setShortcut(_translate("MainWindow", "Ctrl+O"))
    self.actionSave.setText(_translate("MainWindow", "Save"))
    self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))

#####################################################################################################################