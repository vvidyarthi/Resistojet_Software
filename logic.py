import sys
import time
import qtmodules
from BSS import data_logger
import BSS
from BSS_lab_equipment import flocat, Sorensen, USB_TEMP_AI
#from PyQt6.QtCore import QApplication, QWidget, QMainWindow


# Empty Arrays to hold data for plotting
time_array = []
tc1_array = []
tc2_array = []
tc3_array = []
tc4_array = []
flow_array = []
voltage_array = []
current_array = []
power_array = []

def setup():
    '''
    Function to connect to the various sensors and opens a log file
    '''
    global cat
    global logger
    global psu
    global tcdaq
    global tc1
    global tc2
    global tc3
    global tc4
    global column_names
    try:
        # Alicat
        cat = flocat.Flocat(port="/dev/ttyUSB1", event_log_name="/dev/null", baudrate=115200,logging_level = "info")
        # Power Source
        psu = Sorensen.Sorensen(port="/dev/ttyUSB2")
        # Thermocouples
        tcdaq = USB_TEMP_AI.TcDaq()

        column_names=["Time [s]",
                "TC1 [C]",
                "TC2 [C]",
                "TC3 [C]",
                "TC4 [C]",
                "Flow rate [SLPM]",
                "Heater Status",
                "Voltage [V]",
                "Current [A]",
                "Power [W]"]
    except:
        print("Was unable to connect to one or more of the devices")

def collect_data():
    '''
    Collects data from the thermocouples, alicat, and psu and appends them
    into the empty arrays at the beginning of the document for plotting
    '''

    global data_array


    current_time = time.time()
    current_read = psu.get_current()
    voltage_read = psu.get_voltage()
    power_read = current_read*voltage_read
    
    # Thermocouple data acquisition
    
    try:
        tc1 = tcdaq.get_temp(0)
    except ULException as e:
        if e.error_code == ULError.OPEN_CONNECTION:
            print("Open connection on TC1")

    try:
        tc2 = tcdaq.get_temp(1)
    except ULException as e:
        if e.error_code == ULError.OPEN_CONNECTION:
            print("Open connection on TC2")
    try:
        tc3 = tcdaq.get_temp(2)
    except ULException as e:
        if e.error_code == ULError.OPEN_CONNECTION:
            print("Open connection on TC3")
  
    try:
        tc4 = tcdaq.get_temp(3)
    except ULException as e:
        if e.error_code == ULError.OPEN_CONNECTION:
            print("Open connection on TC4")
        

    # Alicat Data Acquisition
    try:
        flow = cat.get_data()[4]
    except:
        flow = 1
    # Putting Data into an array and saving to the file
    data_array = (current_time, tc1, tc2, tc3, tc4, flow, voltage_read, current_read, power_read)
    # Appending into the arrays
    time_array.append(current_time)
    tc1_array.append(tc1)
    tc2_array.append(tc2)
    tc3_array.append(tc3)
    tc4_array.append(tc4)
    flow_array.append(flow)
    voltage_array.append(voltage_read)
    current_array.append(current_read)
    power_array.append(power_read)
    
    
    print(f'tc1: {tc1:<10.3f}  tc2: {tc2:<10.3f}  tc3: {tc3:<10.3f}   tc4: {tc4:<10.3f}')

        


def control_loop(target_temperature, voltage):
    '''
    Controls the PSU and modulates the temperature at a target temp
    '''
    psu.set_voltage(voltage)

    if tc1 < (target_temperature + 5):
        psu.set_power_on()
    elif tc1 > (target_temperature-5):
        psu.set_power_off()
def lifetime_loop(num_cycles, voltage, target_time, target_temp, low_temp, low_time):
    iterator = 0 
    fire_state = 1
    idle_state = 0
    psu.set_voltage(voltage)

    while iterator < num_cycles:
        while fire_state == 1 and idle_state == 0:
            # Making sure that the system is in the start state
            while tc1 < (target_temp - 5):
                # Heating up to operation temperature
                psu.set_power_on()

            # Start time to calculate run time at target temp
            start_time = time.time()
            while target_time >= (time.time()-start_time):
                if tc1 < (target_temp - 5):
                    psu.set_power_on()
                elif tc1 > target_temp:
                    psu.set_power_off()

            #Setting Fire state to off to signal the completion of time at 
            #target temp
            fire_state = 0
            idle_state = 1
        while fire_state == 0 and idle_state == 1:
            while tc1 > low_temp + 5:
                psu.set_power_off()
            
            start_time = time.time()
            while low_time >= (time.time()-start_time):
                if tc < (low_temp - 10):
                    psu.set_power_on()
                elif tc > (low_temp + 10):
                    psu.set_power_off()
                fire_state = 1
                idle_state = 0
                








