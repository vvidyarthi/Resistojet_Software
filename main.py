import sys

import containers
import qtconfig
from qtconfig import *
from containers import *
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow)
from PySide6.QtCore import QThread


class Worker(QThread):
    def run(self):

        while True:
            
            collector_.collect_data()
            if state_.control_state == 1 and state_.lifetime_state == 0:
                controller_.control_loop(state_.target_temp, state_.target_temp, collector_.tc1_array)
                widget_.logger.log_data(collector_.data_array)
            elif state_.control_state == 0 and state_.lifetime_state == 1:
                print("No Lifetime State Currently Implemented")
            
            plotter_.plot_data(collector_.time_array, collector_.tc1_array, collector_.tc2_array,
                            collector_.flow_array, collector_.voltage_array, collector_.power_array)


class MainWindow(QMainWindow):

    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.worker = None
        self.background_task()
        self.setWindowTitle("Benchmark Space Systems Resistojet Software")
        self.setCentralWidget(widget)

    def background_task(self):
        self.worker = Worker()
        # self.worker.started.connect(self.worker.run)
        self.worker.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    state_ = containers.StateContainer()
    
    collector_ = containers.DataContainer()
    collector_.setup()
    controller_ = containers.ControlContainer(collector_.psu)
    widget_ = qtconfig.Widget(state_, controller_)
    plotter_ = containers.Plotter(widget_)
    
    window = MainWindow(widget_)
    window.resize(1080, 900)

    window.show()
    sys.exit(app.exec())