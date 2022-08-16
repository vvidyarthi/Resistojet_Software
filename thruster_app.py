from logic import *
from qtmodules import *
from PyQt5 import QtCore
from time import sleep
from PyQt5.QtCore import QObject, QThread, pyqtSignal


class worker(QThread):

    def run(self):

        # data_array = pyqtSignal()
        state_ = StateContainer()
        collector = DataContainer()
        controller = ControlContainer()

        collector.setup()

        while True:

            collector.collect_data()
            if state_.control_state == 1 and state_.lifetime_state == 0:
                controller.control_loop(state.target_temp, state.voltage)
                widget.logger.log_data(collector.data_array)
            elif state_.lifetime_state == 1 and state_.control_state == 0:
                print("Lifetime Testing Not Implemented Yet")

            widget.thermal_canvas.axes.cla()
            widget.flow_canvas.axes.cla()
            widget.electric_canvas.axes.cla()

            widget.thermal_canvas.axes.plot(collector.time_array, collector.tc1_array)
            widget.thermal_canvas.axes.plot(collector.time_array, collector.tc2_array)
            # widget.thermal_canvas.axes.plot(time_array, tc3_array)

            widget.flow_canvas.axes.plot(collector.time_array, collector.flow_array)

            widget.electric_canvas.axes.plot(collector.time_array, collector.voltage_array)
            widget.electric_canvas.axes.plot(collector.time_array, collector.power_array)

            widget.thermal_canvas.draw()
            widget.flow_canvas.draw()
            widget.electric_canvas.draw()
            sleep(0.5)


class MainWindow(QMainWindow):

    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.worker = worker()
        self.collection_task()
        self.setWindowTitle("Benchmark Space Systems Resistojet Software")
        self.setCentralWidget(widget)

        # self.update_canvas()

        # self.timer = QtCore.QTimer()
        # self.timer.setInterval(50)
        # self.timer.timeout.connect(self.update_canvas)
        # self.timer.start()

        # self.update_plot(widget)

    def collection_task(self):
        self.worker.started.connect(self.worker.run)
        self.worker.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget_ = Widget()

    window = MainWindow(widget_)
    window.resize(1000, 900)

    window.show()
    sys.exit(app.exec())
