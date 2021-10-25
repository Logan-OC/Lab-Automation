import pyvisa

#my_instrument.read_termination = '\n'##########
#my_instrument.write_termination = '\n' ##############
#print(rm.list_resources())
#print(my_instrument.query('*IDN?'))

class main(object):
    #On initialisation connects to instrument's serial address and begins waiting for commands
    def __init__(self,serial_addr):
        self.rm = pyvisa.ResourceManager()
        self.my_instrument = self.rm.open_resource(serial_addr)
        self.read_command()

    #Function reads from SSH terminal and prints a response
    def read_command(self):
        while True:
            command_input = input()
            self.send_command(command_input)
            #print(command_input)

    #Function writes data to instrument and reads the response       
    def send_command(self, command):
        try:
            if '?' in command:
                response = self.my_instrument.query(command)    #Queries instrument if command ends in ?
                return response                                 #Otherwise just writes to instrument
            else:
                self.my_instrument.write(command)
                return True      
        except:
            return False


        
    
if __name__ == "__main__":

    #Program starts by waiting for an input with the serial address
    serial_addr = input()
    print('serial working')  

    #Class is initialised with the serial address
    a = main(serial_addr)