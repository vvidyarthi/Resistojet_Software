'''
Handles all of the Qt modules and graph displays
'''
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
        QApplication,
        QMainWindow,
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
from matplotlib.backends.backend_qt import FigureCanvasQT
from matplotlib.figure import Figure

class MplCanvas(FigureCanvasQT):
    '''
    Class manages the creation of empty matplotlib plots
    '''

    def __init__(self, width = 900, height = 400, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class Widget(QWidget):
    '''
    Class sets up the various components in the window and organizes them 
    '''

    def __init__(self):
        QWidget.__init__(self)

        # Inputs
        self.filename = QLineEdit()
        self.voltage_input = QLineEdit()
        self.preheat_time = QLineEdit()
        self.target_temp = QLineEdit()

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
        self.userside.addWidget(QLabel("Target Temp [C]"))
        self.userside.addWidget(self.target_temp)
        
        self.cycling = QGridLayout()
        self.spaceItem = QSpacerItem(150,10, QSizePolicy.Expanding)
        self.cycling.addWidget(self.box)
        self.cycling.addItem(self.spaceItem, 1,1, 1,1)

        self.cycling.addWidget(QLabel('Number of Cycles:'))
        self.cycling.addItem(self.spaceItem, 1,3, 1,1)
        self.cycling.addWidget(self.cycles)

        self.cycling.addWidget(QLabel('Input Voltage:'))
        self.cycling.addItem(self.spaceItem, 1,3, 1,1)
        self.cycling.addWidget(self.cycle_voltage)

        self.cycling.addWidget(QLabel('Time at Target Temp:'))
        self.cycling.addItem(self.spaceItem, 1,3, 1,1)
        self.cycling.addWidget(self.cycle_on_time)

        self.cycling.addWidget(QLabel('Time at Low Temp:'))
        self.cycling.addItem(self.spaceItem, 1,3, 1,1)
        self.cycling.addWidget(self.cycle_off_time)

        self.cycling.addWidget(QLabel('Target Temp:'))
        self.cycling.addItem(self.spaceItem, 1,2, 1,1)
        self.cycling.addWidget(self.cycle_target_temp)
        
        self.cycling.addWidget(QLabel('Off Temp:'))
        self.cycling.addItem(self.spaceItem, 1,2, 1,1)
        self.cycling.addWidget(self.ambient_temp)

        self.buttons = QVBoxLayout()
        self.buttons.addWidget(self.start)
        self.buttons.addWidget(self.end)

        # Matplots

        self.thermocouple_plot = MplCanvas(width = 900, height = 400, dpi = 100)
        self.massflow_plot = MplCanvas(width = 900, height = 400, dpi = 100)
        self.electric_plot = MplCanvas(width = 900, height = 400, dpi = 100)
        self.tableside = QVBoxLayout()
        self.tableside.addWidget(QLabel("Thermocouples"))
        self.tableside.addWidget(thermocouple_plot)
        self.tableside.addWidget(QLabel("Mass Flow"))
        self.tableside.addWidget(massflow_plot)
        self.tableside.addWidget(QLabel("Power and Voltages"))
        self.tableside.addWidget(electric_plot)



        self.layout = QVBoxLayout()
        self.layout.addLayout(self.userside)
        self.layout.addLayout(self.cycling)
        self.layout.addLayout(self.buttons)
        self.layout.addLayout(self.tableside)


        self.setLayout(self.layout)

        self.start.clicked.connect(self.exstart)
        self.end.clicked.connect(self.exend)


        # Disabling inputs depending on the checkbox

        self.filename.setEnabled(self.box.checkState()==Qt.Unchecked)
        self.voltage_input.setEnabled(self.box.checkState()==Qt.Unchecked)
        self.preheat_time.setEnabled(self.box.checkState()==Qt.Unchecked)
        self.target_temp.setEnabled(self.box.checkState()==Qt.Unchecked)

        self.cycles.setEnabled(self.box.checkState()!=Qt.Unchecked)
        self.cycle_voltage.setEnabled(self.box.checkState()!=Qt.Unchecked)
        self.cycle_on_time.setEnabled(self.box.checkState()!=Qt.Unchecked)
        self.cycle_off_time.setEnabled(self.box.checkState()!=Qt.Unchecked)
        self.cycle_target_temp.setEnabled(self.box.checkState()!=Qt.Unchecked)
        self.ambient_temp.setEnabled(self.box.checkState()!=Qt.Unchecked)
            
        self.box.stateChanged.connect(lambda state:
            self.voltage_input.setEnabled(self.box.checkState()==Qt.Unchecked))
        self.box.stateChanged.connect(lambda state:
            self.preheat_time.setEnabled(self.box.checkState()==Qt.Unchecked))
        self.box.stateChanged.connect(lambda state:
            self.target_temp.setEnabled(self.box.checkState()==Qt.Unchecked))
        self.box.stateChanged.connect(lambda state:
            self.cycles.setEnabled(self.box.checkState()!=Qt.Unchecked))
        self.box.stateChanged.connect(lambda state:
            self.cycle_voltage.setEnabled(self.box.checkState()!=Qt.Unchecked))
        self.box.stateChanged.connect(lambda state:
            self.cycle_on_time.setEnabled(self.box.checkState()!=Qt.Unchecked))
        self.box.stateChanged.connect(lambda state:
            self.cycle_off_time.setEnabled(self.box.checkState()!=Qt.Unchecked))
        self.box.stateChanged.connect(lambda state:
            self.cycle_target_temp.setEnabled(self.box.checkState()!=Qt.Unchecked))
        self.box.stateChanged.connect(lambda state:
            self.ambient_temp.setEnabled(self.box.checkState()!=Qt.Unchecked))

    @Slot()
    def exstart(self):
        filename = self.filename.text()
        voltage = float(self.voltage_input.text())
        preheat = float(self.preheat_time.text())
        target_temp = float(self.target_temp.text())

        self.filename.setReadOnly(True)
        self.voltage_input.setReadOnly(True)
        self.preheat_time.setReadOnly(True)
        self.target_temp.setReadOnly(True)
        self.cycles.setReadOnly(True)
        self.cycle_voltage.setReadOnly(True)
        self.cycle_on_time.setReadOnly(True)
        self.cycle_off_time.setReadOnly(True)
        self.cycle_target_temp.setReadOnly(True)
        self.ambient_temp.setReadOnly(True)

        print('Start: %s' %filename)
        print('Voltage: %f' %voltage)
        print('Preheat Time: %f' %preheat)
        print('Target Temp: %f' %target_temp)





    @Slot()
    def exend(self):
        print('Clicked End')
        self.filename.setReadOnly(False)
        self.voltage_input.setReadOnly(False)
        self.preheat_time.setReadOnly(False)
        self.target_temp.setReadOnly(False)


class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("Benchmark Space Systems Resistojet Software")
        self.setCentralWidget(widget)
