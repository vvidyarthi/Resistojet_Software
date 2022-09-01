import time
import sys
import containers
import qtconfig
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow)
from PySide6.QtCore import QObject, QThread


class Worker(QObject):

    def __init__(self):
        self.init_time = time.time()
        QObject.__init__(self)
    
    def run(self):
        while True:
            time.sleep(0.1)

            if state_.control_state == 0:
                pass

            elif state_.control_state == 1:
                controller_.control_normal(state_.target_temp, state_.fire_temp, state_.voltage, collector_.tc1_array, collector_.flow_array)
                widget_.logger.log_data(collector_.data_array)
        
            elif state_.control_state == 2:
                controller_.control_lifetime(state_.cycle_number, state_.voltage, state_.high_temp, state_.low_temp, state_.high_time, state_.low_time, collector_.tc1_array)
                widget_.logger.log_data(collector_.data_array)

class DataWorker(QObject):
    def __init__(self):
        self.init_time = time.time()
        QObject.__init__(self)

    def run(self):
        time.sleep(0.1)
        collector_.collect_data(self.init_time)
        print(f'tc1: {collector_.tc1:<10.3f}  tc2: {collector_.tc2:<10.3f}  tc3: {collector_.tc3:<10.3f}   tc4: {collector_.tc4:<10.3f}')
        plotter_.plot_data(collector_.time_array, collector_.tc1_array, collector_.tc2_array, collector_.flow_array, collector_.voltage_array, collector_.power_array)

class MainWindow(QMainWindow):

    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.worker = None
        self.data_worker = None
        self.thread = None
        self.data_thread = None

        self.data_task()
        self.worker_task()
        self.setWindowTitle("Benchmark Space Systems Resistojet Software")
        self.setCentralWidget(widget)

    def worker_task(self):
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def data_task(self):
        self.data_thread = QThread()
        self.data_worker = DataWorker()
        self.data_worker.moveToThread(self.data_thread)
        self.data_thread.started.connect(self.data_worker)
        self.data_thread.start()


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
