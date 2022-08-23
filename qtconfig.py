'''
Handles all of the Qt modules and graph displays
'''
import imp
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QVBoxLayout,
    QGridLayout,
    QWidget,
    QSizePolicy,
    QCheckBox,
    QLabel,
    QPushButton,
    QSpacerItem,
    QHBoxLayout,
    QLineEdit)

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from BSS import data_logger

matplotlib.use('Qt5Agg')


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=7, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot()
        super(MplCanvas, self).__init__(fig)


class Widget(QWidget):
    """
    Class sets up the various components in the window and organizes them
    """

    def __init__(self, state_container, control_container):
        QWidget.__init__(self)

        self.state_ = state_container
        self.controller_ = control_container
        self.logger = None

        # Inputs
        self.filename = QLineEdit()
        self.voltage_input = QLineEdit()
        self.preheat_time = QLineEdit()
        self.target_temp = QLineEdit()
        self.fire_temp = QLineEdit()

        # Cycling Inputs
        self.box = QCheckBox('Cycling')
        self.cycles = QLineEdit()
        self.cycle_voltage = QLineEdit()
        self.cycle_on_time = QLineEdit()
        self.cycle_off_time = QLineEdit()
        self.cycle_target_temp = QLineEdit()
        self.ambient_temp = QLineEdit()

        # Buttons
        self.start = QPushButton("Start")
        self.end = QPushButton("End")

        self.userside = QHBoxLayout()

        self.userside.addWidget(QLabel("File Name"))
        self.userside.addWidget(self.filename)
        self.userside.addWidget(QLabel("Input Voltage [V]:"))
        self.userside.addWidget(self.voltage_input)
        self.userside.addWidget(QLabel("Preheat Time [s]:"))
        self.userside.addWidget(self.preheat_time)
        self.userside.addWidget(QLabel("Target Temp [C]:"))
        self.userside.addWidget(self.target_temp)
        self.userside.addWidget(QLabel("Firing Temperature [C]:"))
        self.userside.addWidget(self.fire_temp)

        self.cycling = QGridLayout()
        self.spaceItem = QSpacerItem(150, 10, QSizePolicy.Expanding)
        self.cycling.addWidget(self.box)

        self.cycling.addWidget(QLabel('Number of Cycles:'))
        self.cycling.addWidget(self.cycles, 1, 2)

        self.cycling.addWidget(QLabel('Input Voltage:'))
        self.cycling.addWidget(self.cycle_voltage, 2, 2)

        self.cycling.addWidget(QLabel('Time at Target Temp:'))
        self.cycling.addWidget(self.cycle_on_time, 3, 2)

        self.cycling.addWidget(QLabel('Time at Low Temp:'))
        self.cycling.addWidget(self.cycle_off_time, 4, 2)

        self.cycling.addWidget(QLabel('Target Temp:'))
        self.cycling.addWidget(self.cycle_target_temp, 5, 2)

        self.cycling.addWidget(QLabel('Off Temp:'))
        self.cycling.addWidget(self.ambient_temp, 6, 2)

        self.buttons = QVBoxLayout()
        self.buttons.addWidget(self.start)
        self.buttons.addWidget(self.end)

        # Matplots

        self.thermal_canvas = MplCanvas(self, width=8, height=7, dpi=90)
        self.flow_canvas = MplCanvas(self, width=8, height=7, dpi=90)
        self.electric_canvas = MplCanvas(self, width=8, height=7, dpi=90)

        self.tableside = QVBoxLayout()
        self.tableside.addWidget(QLabel("Thermocouples"))
        self.tableside.addWidget(self.thermal_canvas)
        self.tableside.addWidget(QLabel("Mass Flow"))
        self.tableside.addWidget(self.flow_canvas)
        self.tableside.addWidget(QLabel("Power and Voltages"))
        self.tableside.addWidget(self.electric_canvas)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.userside)
        self.layout.addLayout(self.cycling)
        self.layout.addLayout(self.buttons)
        self.layout.addLayout(self.tableside)

        self.setLayout(self.layout)

        self.start.clicked.connect(self.qtstart)
        self.end.clicked.connect(self.qtend)

        # Disabling inputs depending on the checkbox

        self.filename.setEnabled(self.box.checkState() == Qt.Unchecked)
        self.voltage_input.setEnabled(self.box.checkState() == Qt.Unchecked)
        self.preheat_time.setEnabled(self.box.checkState() == Qt.Unchecked)
        self.target_temp.setEnabled(self.box.checkState() == Qt.Unchecked)
        self.fire_temp.setEnabled(self.box.checkState() == Qt.Unchecked)

        self.cycles.setEnabled(self.box.checkState() != Qt.Unchecked)
        self.cycle_voltage.setEnabled(self.box.checkState() != Qt.Unchecked)
        self.cycle_on_time.setEnabled(self.box.checkState() != Qt.Unchecked)
        self.cycle_off_time.setEnabled(self.box.checkState() != Qt.Unchecked)
        self.cycle_target_temp.setEnabled(self.box.checkState() != Qt.Unchecked)
        self.ambient_temp.setEnabled(self.box.checkState() != Qt.Unchecked)

        self.box.stateChanged.connect(lambda state:
                                      self.voltage_input.setEnabled(self.box.checkState() == Qt.Unchecked))
        self.box.stateChanged.connect(lambda state:
                                      self.preheat_time.setEnabled(self.box.checkState() == Qt.Unchecked))
        self.box.stateChanged.connect(lambda state:
                                      self.target_temp.setEnabled(self.box.checkState() == Qt.Unchecked))
        self.box.stateChanged.connect(lambda state:
                                      self.cycles.setEnabled(self.box.checkState() != Qt.Unchecked))
        self.box.stateChanged.connect(lambda state:
                                      self.cycle_voltage.setEnabled(self.box.checkState() != Qt.Unchecked))
        self.box.stateChanged.connect(lambda state:
                                      self.cycle_on_time.setEnabled(self.box.checkState() != Qt.Unchecked))
        self.box.stateChanged.connect(lambda state:
                                      self.cycle_off_time.setEnabled(self.box.checkState() != Qt.Unchecked))
        self.box.stateChanged.connect(lambda state:
                                      self.cycle_target_temp.setEnabled(self.box.checkState() != Qt.Unchecked))
        self.box.stateChanged.connect(lambda state:
                                      self.ambient_temp.setEnabled(self.box.checkState() != Qt.Unchecked))

    @Slot()
    def qtstart(self):
        self.start.setEnabled(False)
        filename = self.filename.text()
        filename = filename + '.csv'

        column_names = ["Time [s]",
                        "TC1 [C]",
                        "TC2 [C]",
                        "TC3 [C]",
                        "TC4 [C]",
                        "Flow rate [SLPM]",
                        "Voltage [V]",
                        "Current [A]",
                        "Power [W]"]

        self.filename.setReadOnly(True)
        self.voltage_input.setReadOnly(True)
        self.preheat_time.setReadOnly(True)
        self.target_temp.setReadOnly(True)
        self.fire_temp.setReadOnly(True)
        self.cycles.setReadOnly(True)
        self.cycle_voltage.setReadOnly(True)
        self.cycle_on_time.setReadOnly(True)
        self.cycle_off_time.setReadOnly(True)
        self.cycle_target_temp.setReadOnly(True)
        self.ambient_temp.setReadOnly(True)

        if self.box.checkState() == Qt.Unchecked:

            voltage = float(self.voltage_input.text())
            preheat = float(self.preheat_time.text())
            target_temp = float(self.target_temp.text())
            fire_temp = float(self.fire_temp.text())
            self.logger = data_logger.DataLogger(filename, column_names)
            self.state_.control_normal(target_temp, fire_temp, voltage)
        

        elif self.box.checkState() != Qt.Unchecked:

            cycle_voltage = float(self.cycle_voltage.text())
            cycle_on_time = float(self.cycle_on_time.text())
            cycle_off_time = float(self.cycle_off_time.text())
            cycle_target_temp = float(self.cycle_target_temp.text())
            cycle_ambient_temp = float(self.ambient_temp.text())
            num_cycles = int(self.cycles.text())

    @Slot()
    def qtend(self):
        print('Clicked End')
        self.filename.setReadOnly(False)
        self.voltage_input.setReadOnly(False)
        self.preheat_time.setReadOnly(False)
        self.target_temp.setReadOnly(False)
        self.fire_temp.setReadOnly(False)
        self.state_.control_stop()
        # self.controller_.control_shutdown()
        try:
            self.logger.save()
            self.logger.close()
        except (Exception,):
            pass
        self.start.setEnabled(True)

