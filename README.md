# Lab-Automation
Control optical communication lab instruments via a raspberry pi, utilising a graphical user interface. This project is created in python and the GUI is built using the PyQt5 toolbox.  

# Before Running
Change the raspberry pi IP address.

Change raspberry pi username and password if not using default.

Change serial address for each instrument under serial variable at top of Python code.

Upload 'Raspberry pi files' to home directory of raspberry pi

# INFO
The file 'functions_list.py' contains all basic functions used so that you may create a new GUI for another instrument. Details are listed inside

'custom_script_example.py' is an example Python script of how to write code for complex operation of an instrument.
This is meant for sending commands directly to and from the instrument without a GUI.
Write code to sweep through setting values or connect to more instruments.
