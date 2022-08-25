from email.errors import ObsoleteHeaderDefect
from os import stat
import time
import sys
import containers
import qtconfig
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow)
from PySide6.QtCore import QThread, pyqtSignal, QTimer


class Worker(QThread):
    
    time_signal = pyqtSignal(object)
    tc1_signal = pyqtSignal(object)
    tc2_signal = pyqtSignal(object)
    flow_signal = pyqtSignal(object)
    voltage_signal = pyqtSignal(object)
    power_signal = pyqtSignal(object)

    def __init__(self):
        self.init_time = time.time()
        QThread.__init__(self)
    
    def run(self):  
        while True:
            self.data_array = collector_.collect_data(self.init_time)
            self.time_signal.emit(collector_.time_array)
            self.tc1_signal.emit(collector_.tc1_array)
            self.tc2_signal.emit(collector_.tc2_array)
            self.flow_signal.emit(collector_.flow_array)
            self.voltage_signal.emit(collector_.voltage_array)
            self.power_signal.emit(collector_.power_array)

        # plotter_.plot_data(collector_.time_array, collector_.tc1_array, collector_.tc2_array, 
        #     collector_.flow_array, collector_.voltage_array, collector_.power_array)


            if state_.control_state == 0:
                pass

            elif state_.control_state == 1:
                controller_.control_normal(state_.target_temp, state_.fire_temp, state_.voltage, collector_.tc1_array, collector_.flow_array)
                widget_.logger.log_data(collector_.data_array)

            
            elif state_.control_state == 2:
                print("No Lifetime State Currently Implemented")
            

class MainWindow(QMainWindow):

    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.worker = None
        self.data_collecting_worker()
        self.setWindowTitle("Benchmark Space Systems Resistojet Software")
        self.setCentralWidget(widget)

    def data_collecting_worker(self):
        self.worker = Worker()
        self.worker.time_signal.connect(self.display)
        self.worker.tc1_signal.connect(self.display)
        self.worker.tc2_signal.connect(self.display)
        self.worker.flow_signal.connect(self.display)
        self.worker.voltage_signal.connect(self.display)
        self.worker.power_signal.connect(self.display)
        self.worker.start()
        # self.worker.started.connect(self.worker.run)
        # self.worker.start()
        # self.update_timer = QTimer()
        # self.update_timer.setInterval(10)
        # self.update_timer.timeout.connect(self.worker.run)
        # self.update_timer.start()
    def dispay(self):
        plotter_.plot_data(collector_.time_array, collector_.tc1_array, collector_.tc2_array, 
            collector_.flow_array, collector_.voltage_array, collector_.power_array)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    state_ = containers.StateContainer()
    collector_ = containers.DataContainer()
    collector_.setup()
    controller_ = containers.ControlContainer(collector_.psu)
    widget_ = qtconfig.Widget(state_, controller_)
    plotter_ = containers.Plotter(widget_)
    
    window = MainWindow(widget_)
    window.resize(900, 1080)

    window.show()
    sys.exit(app.exec())
