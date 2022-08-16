import sys
import time
from time import sleep
from BSS import data_logger
import BSS
from BSS_lab_equipment import flocat, Sorensen, USB_TEMP_AI


class StateContainer:

    def __init__(self):
        self.control_state = 0
        self.lifetime_state = 0
        self.target_temp = 0
        self.voltage = 0

    def control_starter(self, target_temperature, voltage_input):
        self.control_state = 1
        self.lifetime_state = 0
        self.target_temp = target_temperature
        self.voltage = voltage_input

    def control_stop(self):
        self.control_state = 0
        self.lifetime_state = 0
        # try:
        #     self.logger.save()
        #     self.logger.close()
        # except (Exception,):
        #     pass



class DataContainer:

    def __init__(self):
        self.data_array = None
        self.time_array = []
        self.tc1_array = []
        self.tc2_array = []
        self.tc3_array = []
        self.tc4_array = []
        self.flow_array = []
        self.current_array = []
        self.voltage_array = []
        self.power_array = []
        self.psu = None
        self.cat = None
        self.tcdaq = None
        self.tc1 = None
        self.tc2 = None
        self.tc3 = None
        self.tc4 = None
        self.flow = None

    def setup(self):
        """
        Function to connect to the various sensors and opens a log file
        """

        try:
            # Alicat
            self.cat = flocat.Flocat(port="/dev/ttyUSB1", event_log_name="/dev/null", baudrate=115200,
                                     logging_level="info")
            # Power Source
            self.psu = Sorensen.Sorensen(port="/dev/ttyUSB2")
            # Thermocouples
            self.tcdaq = USB_TEMP_AI.TcDaq()
        except (Exception,):
            print("Was unable to connect to one or more of the devices")

    def collect_data(self):
        """
        Collects data from the thermocouples, alicat, and psu and appends them
        into the empty arrays at the beginning of the document for plotting
        """

        current_time = time.time()
        current_read = self.psu.get_current()
        voltage_read = self.psu.get_voltage()
        power_read = current_read*voltage_read

        # Thermocouple data acquisition

        try:
            self.tc1 = self.tcdaq.get_temp(0)
        except self.ULException as e:
            if e.error_code == self.ULError.OPEN_CONNECTION:
                print("Open connection on TC1")

        try:
            self.tc2 = self.tcdaq.get_temp(1)
        except self.ULException as e:
            if e.error_code == self.ULError.OPEN_CONNECTION:
                print("Open connection on TC2")
        try:
            self.tc3 = self.tcdaq.get_temp(2)
        except self.ULException as e:
            if e.error_code == self.ULError.OPEN_CONNECTION:
                print("Open connection on TC3")

        try:
            self.tc4 = self.tcdaq.get_temp(3)
        except self.ULException as e:
            if e.error_code == self.ULError.OPEN_CONNECTION:
                print("Open connection on TC4")


        # Alicat Data Acquisition
        try:
            self.flow = self.cat.get_data()[4]
        except (Exception,):
            self.flow = 1
        # Putting Data into an array and saving to the file
        self.data_array = (current_time, self.tc1, self.tc2, self.tc3, self.tc4, self.flow, voltage_read, current_read,
                           power_read)
        # Appending into the arrays
        self.time_array.append(current_time)
        self.tc1_array.append(self.tc1)
        self.tc2_array.append(self.tc2)
        self.tc3_array.append(self.tc3)
        self.tc4_array.append(self.tc4)
        self.flow_array.append(self.flow)
        self.voltage_array.append(voltage_read)
        self.current_array.append(current_read)
        self.power_array.append(power_read)

        print(f'tc1: {self.tc1:<10.3f}  tc2: {self.tc2:<10.3f}  tc3: {self.tc3:<10.3f}   tc4: {self.tc4:<10.3f}')


class ControlContainer:
    def __init__(self, psu, tc1_array):
        self.psu = psu
        self.tc1_array = tc1_array
        self.power_flag = 0
        self.voltage_lock = 0

    def control_loop(self, target_temperature, voltage):
        """
            Controls the PSU and modulates the temperature at a target temp
        """

        if self.voltage_lock == 0:
            self.psu.set_voltage(voltage)
            voltage_lock = 1
            sleep(0.2)

        if self.tc1_array[-1] < (target_temperature - 5) and self.power_flag == 0:
            self.psu.set_power_on()
            self.power_flag = 1
        elif self.tc1_array[-1] > (target_temperature - 5) and self.power_flag == 1:
            self.psu.set_power_off()
            self.power_flag = 0

    def shutdown(self, logger):
        self.psu.set_power_off()
        try:
            logger.save()
            logger.close()
        except (Exception,):
            pass

    def lifetime_loop(self,num_cycles, voltage, target_time, target_temp, low_temp, low_time):
        iterator = 0
        fire_state = 1
        idle_state = 0
        self.psu.set_voltage(voltage)

        while iterator < num_cycles:
            while fire_state == 1 and idle_state == 0:
                # Making sure that the system is in the start state
                while self.tc1 < (target_temp - 5):
                    # Heating up to operation temperature
                    self.psu.set_power_on()

                # Start time to calculate run time at target temp
                start_time = time.time()
                while target_time >= (time.time()-start_time):
                    if self.tc1 < (target_temp - 5):
                        self.psu.set_power_on()
                    elif self.tc1 > target_temp:
                        self.psu.set_power_off()

                #Setting Fire state to off to signal the completion of time at
                #target temp
                fire_state = 0
                idle_state = 1
            while fire_state == 0 and idle_state == 1:
                while self.tc1 > low_temp + 5:
                    self.psu.set_power_off()

                start_time = time.time()
                while low_time >= (time.time()-start_time):
                    if self.tc1 < (low_temp - 10):
                        self.psu.set_power_on()
                    elif self.tc1 > (low_temp + 10):
                        self.psu.set_power_off()
                    fire_state = 1
                    idle_state = 0
                








