from BSS_lab_equipment import flocat, Sorensen, USB_TEMP_AI
import time


class StateContainer:
    """
    The StateContainer signals the state that the test is in and passes values to the control container
    """

    def __init__(self):
        # Control State 0 is at idle, 1 is normal firing, and 2 is lifetime tesing
        self.fire_temp = 0
        self.control_state = 0
        self.target_temp = 0
        self.voltage = 0
        self.cycle_number = 0
        self.voltage = 0
        self.low_temp = 0
        self.low_time = 0
        self.high_temp = 0
        self.high_time = 0
        print("Initialized State Containers")

    def control_normal(self, temperature_input, fire_temperature_input, voltage_input):
        self.control_state = 1
        self.target_temp = temperature_input
        self.fire_temp = fire_temperature_input
        self.voltage = voltage_input
        print("Normal Control")

    def control_lifetime(self, cycle_num_inp, voltage_input, low_temp_input, low_time_input, high_temp_input,
                         high_time_input):
        self.control_state = 2
        self.cycle_number = cycle_num_inp
        self.voltage = voltage_input
        self.low_temp = low_temp_input
        self.low_time = low_time_input
        self.high_temp = high_temp_input
        self.high_time = high_time_input
        print("Lifetime Started")

    def control_stop(self):
        self.control_state = 0


class DataContainer:
    """
    The DataContainer holds the arrays of TC, Alicat, and PSU data
    """

    def __init__(self):
        self.ULError = None
        self.ULException = None
        self.psu = None
        self.cat = None
        self.tcdaq = None
        self.data_array = None
        self.tc1 = None
        self.tc2 = None
        self.tc3 = None
        self.tc4 = None
        self.flow = None
        self.pressure = None
        self.alicat_tc = None
        self.time_array = []
        self.tc1_array = []
        self.tc2_array = []
        self.tc3_array = []
        self.tc4_array = []
        self.flow_array = []
        self.pressure_array = []
        self.alicat_tc_array = []
        self.voltage_array = []
        self.current_array = []
        self.power_array = []

    def setup(self):
        """
        Connects to the Alicat, PSU, and TCs
        """
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
        """
        Reads data from Alicat, PSU, and TCs and adds to respective arrays
        """
        current_time = time.time() - start_time
        try:
            current_read = self.psu.get_current()
            voltage_read = self.psu.get_voltage()
            power_read = current_read * voltage_read
        except(Exception,):
            current_read = 0
            voltage_read = 0
            power_read = 0
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
            alicat_data_array = self.cat.get_data()
            self.pressure = alicat_data_array[1]
            self.alicat_tc = alicat_data_array[2]
            self.flow = alicat_data_array[4]
        except (Exception,):
            self.flow = 1
        # Putting Data into an array and saving to the file
        self.data_array = (
            current_time, self.tc1, self.tc2, self.tc3, self.tc4, self.flow, self.pressure, self.alicat_tc,
            voltage_read,
            current_read,
            power_read)
        # Appending into the arrays
        self.time_array.append(current_time)
        self.tc1_array.append(self.tc1)
        self.tc2_array.append(self.tc2)
        self.tc3_array.append(self.tc3)
        self.tc4_array.append(self.tc4)
        self.flow_array.append(self.flow)
        self.pressure_array.append(self.pressure)
        self.alicat_tc_array.append(self.alicat_tc)
        self.voltage_array.append(voltage_read)
        self.current_array.append(current_read)
        self.power_array.append(power_read)

        # print(f'tc1: {self.tc1:<10.3f}  tc2: {self.tc2:<10.3f}  tc3: {self.tc3:<10.3f}   tc4: {self.tc4:<10.3f}')


class Plotter:
    """
    Plots the data arrays on the Matplotlib canvases
    """

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

        self.widget_.thermal_canvas.axes.clear()
        self.widget_.flow_canvas.axes.clear()
        self.widget_.electric_canvas.axes.clear()

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
    """
    Contains the logic to control the PSU for normal tests and lifetime tests
    """

    def __init__(self, psu):
        # Normal Variables Init

        self.psu_ = psu
        self.tc1_array = []
        self.flow_array = []
        self.power_flag = 0
        self.voltage_lock = 0
        self.voltage = 0
        self.voltage_l = 0

        # Lifetime Variables Init
        self.start_time = 0
        self.high_temp_mode = 0
        self.low_temp_mode = 0
        self.cycle_number = 0
        self.num_cycles = 0
        self.high_temp = 0
        self.high_time = 0
        self.low_temp = 0
        self.low_time = 0

    def control_normal(self, target_temperature, fire_temperature, voltage_input, tc1_array_input, flow_array_input):
        self.tc1_array = tc1_array_input
        self.flow_array = flow_array_input
        self.voltage = voltage_input
        if self.voltage_lock == 0:
            self.psu_.set_voltage(self.voltage)
            self.voltage_lock = 1

        # Preheating to the target temperature

        elif self.tc1_array[-1] < target_temperature and self.flow_array[-1] < 0.5 and self.power_flag == 0:
            self.psu_.set_power_on()
            self.power_flag = 1
        elif self.tc1_array[-1] > target_temperature and self.flow_array[-1] < 0.5 and self.power_flag == 1:
            self.psu_.set_power_off()
            self.power_flag = 0

        # Turning on PSU to the firing temperature

        elif self.flow_array[-1] > 0.5 and self.tc1_array[-1] < fire_temperature and self.power_flag == 0:
            self.psu_.set_power_on()
            self.power_flag = 1
        elif self.flow_array[-1] > 0.5 and self.tc1_array[-1] > fire_temperature and self.power_flag == 1:
            self.psu_.set_power_off()
            self.power_flag = 0

    def control_lifetime(self, num_cycles_input, voltage_input, high_temp_input, low_temp_input, high_time_input,
                         low_time_input, tc_array_input):
        self.tc1_array = tc_array_input
        self.num_cycles = num_cycles_input
        self.voltage_l = voltage_input
        self.high_temp = high_temp_input
        self.low_temp = low_temp_input
        self.high_time = high_time_input
        self.low_time = low_time_input
        self.cycle_number = 0
        self.power_flag = 0
        self.start_time = time.time()

        # Setting voltage of the power supply

        if self.voltage_lock == 0:
            self.psu_.set_voltage(self.voltage_l)
            self.voltage_lock = 1

        while self.cycle_number < self.num_cycles:
            # Preheat Mode
            while self.tc1_array[-1] < self.high_temp and self.high_temp_mode == 0 and self.low_temp_mode == 0:
                if self.power_flag == 0:
                    self.psu_.set_power_on()
                    self.power_flag = 1
                else:
                    continue

            # High Temp Mode

            self.psu_.set_power_off()
            self.power_flag = 0
            self.high_temp_mode = 1
            self.low_temp_mode = 0
            self.start_time = time.time()

            while self.high_temp_mode == 1 and self.low_temp_mode == 0 and (
                    time.time() - self.start_time) < self.high_time:
                if self.tc1_array[-1] < self.high_temp and self.power_flag == 0:
                    self.psu_.set_power_on()
                    self.power_flag = 1
                elif self.tc1_array[-1] >= self.high_temp and self.power_flag == 1:
                    self.psu_.set_power_off()
                    self.power_flag = 0

            # Reducing Temp to Low Temp

            while self.tc1_array[-1] > self.low_temp:
                if self.power_flag == 1:
                    self.psu_.set_power_off()
                    self.power_flag = 0
                else:
                    continue

            # Low Temp Mode

            self.psu_.set_power_off()
            self.power_flag = 0
            self.high_temp_mode = 0
            self.low_temp_mode = 1
            self.start_time = time.time()
            while self.low_temp_mode == 1 and self.low_temp == 0 and (time.time() - self.start_time) < self.low_time:
                if self.tc1_array[-1] < self.low_temp and self.power_flag == 0:
                    self.psu_.set_power_on()
                    self.power_flag = 1
                elif self.tc1_array[-1] >= self.low_temp and self.power_flag == 1:
                    self.psu_.set_power_off()
                    self.power_flag = 0

            # Resetting Cycle for New Run
            self.psu_.set_power_off()
            self.power_flag = 0
            self.high_temp_mode = 0
            self.low_temp_mode = 0
            self.cycle_number = self.cycle_number + 1
            continue

    # def control_lifetime(self, num_cycles_input, voltage_input, high_temp_input, low_temp_input, high_time_input,
    #                      low_time_input, tc_array_input):
    #     self.tc1_array = tc_array_input
    #     self.num_cycles = num_cycles_input
    #     self.voltage_l = voltage_input
    #     self.high_temp = high_temp_input
    #     self.low_temp = low_temp_input
    #     self.high_time = high_time_input
    #     self.low_time = low_time_input
    #
    #     if self.voltage_lock == 0:
    #         self.psu_.set_voltage(self.voltage_l)
    #         self.voltage_lock = 1
    #
    #     if self.cycle_number < self.num_cycles:
    #         # Preheating to target temperature
    #
    #         if self.high_temp_mode == 0 and self.low_temp_mode == 0:
    #             if self.tc1_array[-1] < self.high_temp and self.power_flag == 0:
    #                 self.psu_.set_power_on()
    #                 self.power_flag = 1
    #             elif self.tc1_array[-1] > self.high_temp and self.power_flag == 1:
    #                 self.psu_.set_power_off()
    #                 self.power_flag = 0
    #                 self.high_temp_mode = 1
    #
    #         # Starting the target temperature portion of the cycle
    #
    #         if self.high_temp_mode == 1 and self.low_temp_mode == 0 and (
    #                 time.time() - self.start_time) < self.high_time:
    #             if self.tc1_array[-1] < self.high_temp and self.power_flag == 0:
    #                 self.psu_.set_power_on()
    #                 self.power_flag = 1
    #             elif self.tc1_array[-1] > self.high_temp and self.power_flag == 1:
    #                 self.psu_.set_power_off()
    #                 self.power_flag = 0
    #
    #         # Ending the target temperature portion of the cycle and  settling down to the low temperature
    #
    #         elif self.high_temp_mode == 1 and self.low_temp_mode == 0 and (
    #                 time.time() - self.start_time) >= self.high_time:
    #             self.high_temp_mode = 0
    #             self.low_temp_mode = 1
    #             self.start_time = time.time()
    #
    #         # Starting the lower temperature portion of the cycle
    #
    #         if self.high_temp_mode == 0 and self.low_temp_mode == 1 and (time.time() - self.start_time) < self.low_time:
    #             if self.tc1_array[-1] < self.low_temp and self.power_flag == 0:
    #                 self.psu_.set_power_on()
    #                 self.power_flag = 1
    #             elif self.tc1_array[-1] > self.low_temp and self.power_flag == 1:
    #                 self.psu_.set_power_off()
    #                 self.power_flag = 0
    #
    #         # Cycling back to the target temperature portion of the cycle
    #
    #         elif self.high_temp_mode == 0 and self.low_temp_mode == 1 and (
    #                 time.time() - self.start_time) >= self.low_time:
    #             self.high_temp_mode = 1
    #             self.low_temp_mode = 0
    #             self.start_time = time.time()
    #             self.cycle_number = self.cycle_number + 1

    def control_shutdown(self):
        if self.power_flag == 1:
            self.power_flag = 0
            self.low_temp_mode = 0
            self.high_temp_mode = 0
            self.cycle_number = 0
            self.voltage_lock = 0
            self.psu_.set_power_off()
        elif self.power_flag == 0:
            pass
