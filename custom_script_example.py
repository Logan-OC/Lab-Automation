import fiberlabs_EDFA as inst
import os 
import paramiko
import time
import re


serial = 'serial name'
script = 'python3 EDFA.py'

cwd = os.path.dirname(os.path.realpath(__file__))
cwd = cwd + '\\fiberlabs_EDFA.ui'

class main(object):

    #Sends a command over serial
    #If the command expects a response it is True, otherwise False
    def send_command(self, command, response):
            serial_command = command + '\n'  
            
            self.stdin.write(serial_command)
            self.stdin.flush()

            line1 = str(self.stdout.readline()) #Ignore input line when reading
            if response:
                timeout = time.time() + 5       #Waits 5 seconds for a response then timesout
                while time.time() < timeout:
                    line2 = str(self.stdout.readline())
                    data = line2.splitlines()[0]
                    self.input_flag = 1
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


         


if __name__ == "__main__":  
    #Initialise the class, set-up SSH connection and send the serial of the devide to connect to
    a = main()
    a.ssh_setup()
    a.send_command(serial, True)

    ############################################################################################
    #Build custom script from here:

    #Example:
    response=a.send_command('msa::edfa>set_mode p 14.00',True)
    print(response)


    #Close SSH connection when finished
    a.ssh.close()

    
    
    
    
    
        
        

