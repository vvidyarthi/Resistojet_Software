from BSS_lab_equipment import  flocat, Sorensen, USB_TEMP_AI
import time


class StateContainer:
    def __init__(self):
        # Control State 0 is at idle, 1 is normal firing, and 2 is lifetime tesing
        self.control_state = 0
        self.target_temp = 0
        self.voltage = 0
        print("Initialized State Containers")

    def control_normal(self, temperature_input, fire_temperature_input, voltage_input):
        self.control_state = 1
        self.target_temp = temperature_input
        self.fire_temp = fire_temperature_input
        self.voltage = voltage_input
        print("Normal Control")
    
    def control_lifetime(self, cycle_num_inp, low_temp_inp, low_time_inp, high_temp_inp, high_time_inp):
        self.control_state = 3
        self.cycle_number = cycle_num_inp
        self.low_temperature = low_temp_inp
        self.low_time = low_time_inp
        self.high_temp = high_temp_inp
        self.high_time = high_time_inp

        print("Lifetime Started")

    def control_stop(self):
        self.control_state = 0
        print("Control Stopped")


class DataContainer:
    def __init__(self):
        self.psu = None
        self.cat = None
        self.tcdaq = None
        self.data_array = None
        self.tc1 = None
        self.tc2 = None
        self.tc3 = None
        self.tc4 = None
        self.flow = None
        self.time_array = []
        self.tc1_array = []
        self.tc2_array = []
        self.tc3_array = []
        self.tc4_array = []
        self.flow_array = []
        self.voltage_array = []
        self.current_array = []
        self.power_array = []

    def setup(self):
        try:
            # Alicat
            self.cat = flocat.Flocat(port="/dev/ttyUSB2", event_log_name="/dev/null", baudrate=115200,
                                     logging_level="info")
            # Power Source
            self.psu = Sorensen.Sorensen(port="/dev/ttyUSB0")
            # Thermocouples
            self.tcdaq = USB_TEMP_AI.TcDaq()
        except (Exception,):
            print("Was unable to connect to one or more of the devices")

    def collect_data(self, start_time):
        current_time = time.time()-start_time
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


class Plotter:
    def __init__(self, widget):
        self.widget_ = widget
        self.time_array_ = None
        self.tc1_array_ = None
        self.tc2_array_ = None
        self.flow_array_ = None
        self.voltage_array_ = None
        self.power_array_ = None

    def plot_data(self, time_array, tc1_array, tc2_array, flow_array, voltage_array, power_array):
        self.time_array_ = time_array
        self.tc1_array_ = tc1_array
        self.tc2_array_ = tc2_array
        self.flow_array_ = flow_array
        self.voltage_array_ = voltage_array
        self.power_array_ = power_array

        self.widget_.thermal_canvas.axes.cla()
        self.widget_.flow_canvas.axes.cla()
        self.widget_.electric_canvas.axes.cla()

        self.widget_.thermal_canvas.axes.plot(
            self.time_array_, self.tc1_array_)
        self.widget_.thermal_canvas.axes.plot(
            self.time_array_, self.tc2_array_)

        self.widget_.flow_canvas.axes.plot(
            self.time_array_, self.flow_array_)
        self.widget_.electric_canvas.axes.plot(
            self.time_array_, self.voltage_array_)
        self.widget_.electric_canvas.axes.plot(
            self.time_array_, self.power_array_)

        self.widget_.thermal_canvas.draw()
        self.widget_.flow_canvas.draw()
        self.widget_.electric_canvas.draw()


class ControlContainer:
    def __init__(self, psu):
        self.psu_ = psu
        self.tc1_array = []
        self.power_flag = 0
        self.voltage_lock = 0

    def control_normal(self, target_temperature, fire_temperature, voltage, tc1_array_input, flow_array_input):
        self.tc1_array = tc1_array_input
        self.flow_array = flow_array_input
        
        if self.voltage_lock == 0:
            self.psu_.set_voltage(voltage)
            self.voltage_lock = 1

        elif self.tc1_array[-1] < target_temperature and self.flow_array < 0.5 and self.power_flag == 0:
            self.psu_.set_power_on()
            self.power_flag = 1
        elif self.tc1_array[-1] > target_temperature and self.flow_array > 0.5 and self.power_flag == 1:
            self.psu_.set_power_off()
            self.power_flag = 0
        elif self.flow_array > 0.5 and self.tc1_array[-1] < fire_temperature and self.power_flag == 0:
            self.psu_.set_power_on()
            self.power_flag = 1
        elif self.flow_array > 0.5 and self.tc1_array[-1] > fire_temperature and self.power_flag == 1:
            self.psu_.set_power_off()
            self.power_flag = 0

    def control_shutdown(self):
        self.psu_.set_power_off()
        self.psu_.set_voltage(0)
        self.power_flag = 0
        self.voltage_lock = 0
