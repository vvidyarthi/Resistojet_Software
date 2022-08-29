from os import stat
import time
import sys
import containers
import qtconfig
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow)
from PySide6.QtCore import QObject, QThread, QTimer


class Worker(QObject):

    def __init__(self):
        self.init_time = time.time()
        QObject.__init__(self)
    
    def run(self):
        while True:
            time.sleep(0.01)
            collector_.collect_data(self.init_time)

            if state_.control_state == 1:
                controller_.control_normal(state_.target_temp, state_.fire_temp, state_.voltage, collector_.tc1_array, collector_.flow_array)
                widget_.logger.log_data(collector_.data_array)

        
            elif state_.control_state == 2:
                print("No Lifetime State Currently Implemented")
            
            print(f'tc1: {collector_.tc1:<10.3f}  tc2: {collector_.tc2:<10.3f}  tc3: {collector_.tc3:<10.3f}   tc4: {collector_.tc4:<10.3f}')
            plotter_.plot_data(collector_.time_array, collector_.tc1_array, collector_.tc2_array, collector_.flow_array, collector_.voltage_array, collector_.power_array)

class MainWindow(QMainWindow):

    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.worker = None
        self.background_task()
        self.setWindowTitle("Benchmark Space Systems Resistojet Software")
        self.setCentralWidget(widget)

    def background_task(self):
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        # self.update_timer = QTimer()
        # self.update_timer.setInterval(500)
        # self.update_timer.timeout.connect(self.worker.run)
        # self.update_timer.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    state_ = containers.StateContainer()
    collector_ = containers.DataContainer()
    collector_.setup()
    controller_ = containers.ControlContainer()#collector_.psu)
    widget_ = qtconfig.Widget(state_, controller_)
    
    plotter_ = containers.Plotter(widget_)
    
    window = MainWindow(widget_)
    window.resize(900, 1080)

    window.show()
    sys.exit(app.exec())
