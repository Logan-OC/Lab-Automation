import serial

class main(object):
    #On initialisation connects to instrument's serial address and begins waiting for commands
    def __init__(self,serial_addr):
        self.ser = serial.Serial(port = serial_addr, baudrate = 9600, timeout = 5)
        self.read_command()

    #Function reads from SSH terminal and prints a response
    def read_command(self):
        while True:
            command_input = input()
            response = self.send_command(command_input)
            print(response)
            
                
    #Function writes data to instrument and reads the response
    def send_command(self, command):
        
        command = command + '\r\n' #Adds end-of-line characters
        encoded_command = command.encode(encoding='ascii', errors='ignore')
        self.ser.write(encoded_command)
        self.ser.flush()

        try:
            raw_data = self.ser.read_until(b'\r\n') #Reads until end-of-line characters
            data = raw_data.decode('ascii')
            
            return data
        except:
            return False

if __name__ == "__main__":

    #Program starts by waiting for an input with the serial address
    serial_addr = input()
    print('serial working')  

    #Class is initialised with the serial address
    a = main(serial_addr)