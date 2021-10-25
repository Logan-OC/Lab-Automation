import sys
import os 
from PyQt5 import QtWidgets, uic
import subprocess




cwd = os.path.dirname(os.path.realpath(__file__))
si = subprocess.STARTUPINFO()
si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
si.wShowWindow = subprocess.SW_HIDE # default

CREATE_NO_WINDOW = 0x08000000

class Ui(QtWidgets.QMainWindow):
    
    def __init__(self):
        
        super(Ui, self).__init__()
        uic.loadUi(cwd + '\\ICmain.ui', self)
        self.show()

        self.pushButton_1.clicked.connect(lambda:self.open('N7751A.py'))
        self.pushButton_2.clicked.connect(lambda:self.open('N7762A.py'))
        self.pushButton_3.clicked.connect(lambda:self.open('TLG-300.py'))
        self.pushButton_4.clicked.connect(lambda:self.open('fiberlabs_EDFA.py'))
        self.pushButton_5.clicked.connect(lambda:self.open('lightwaves2020_EDFA.py'))
        

    def open(self, file):
        subprocess.Popen(f'start /wait pythonw {cwd}\{file}', shell=True)

    
    #Prompts the user bvefore exiting
    def closeEvent(self,event):
        result = QtWidgets.QMessageBox.question(self,
                      "Confirm Exit...",
                      "Are you sure you want to exit ?",
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)
        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            event.accept()



if __name__ == "__main__":       
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
