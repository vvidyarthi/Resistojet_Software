from logic import *
from qtmodules import *
from PyQt5.QtCore import QObject, QThread, pyqtSignal


class worker(QThread):
    def run(self):
        data_array = pyqtSignal()
        #while True:
            #collect_data()
            #self.data_array.emit()




class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("Benchmark Space Systems Resistojet Software")
        self.setCentralWidget(widget)
        self.collection_task()
        self.update_plot()

    def collection_task(self):
        self.worker = worker()
        self.worker.started.connect(self.worker.run)
        self.worker.start()


    def update_plot(self,widget):
        self.widget.thermocouple_plot.plot(time_array, tc1_array)
        self.widget.thermocouple_plot.plot(time_array, tc2_array)
        self.widget.thermocouple_plot.plot(time_array, tc3_array)

        self.widget.massflow_plot.plot(time_array, flow_array)
        self.widget.electric_plot.plot(time_array, voltage_array)
        self.widget.electric_plot.plot(time_array, power_array)
        self.widget.thermocouple_plot.draw()
        self.widget.massflow_plot.draw()
        self.widget.electric_plot.draw()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    setup()
    widget = Widget()
    window = MainWindow(widget)
    window.resize(1000,900)



    window.show()
    sys.exit(app.exec())
