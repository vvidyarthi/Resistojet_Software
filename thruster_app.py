from logic import *
from qtmodules import *
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QThread, pyqtSignal


class worker(QThread):
    def run(self):
        data_array = pyqtSignal()
        updater=Widget()

        while True:
            collect_data()
            widget.thermal_canvas.axes.cla()
            widget.flow_canvas.axes.cla()
            widget.electric_canvas.axes.cla()

            widget.thermal_canvas.axes.plot(time_array, tc1_array)
            widget.thermal_canvas.axes.plot(time_array, tc2_array)
            widget.thermal_canvas.axes.plot(time_array, tc3_array)

            widget.flow_canvas.axes.plot(time_array,flow_array)

            widget.electric_canvas.axes.plot(time_array, voltage_array)
            widget.electric_canvas.axes.plot(time_array, power_array)

            widget.thermal_canvas.draw()
            widget.flow_canvas.draw()
            widget.electric_canvas.draw()

            #collect_data.data_array.emit()




class MainWindow(QMainWindow):
    global time_array
    global tc1_array
    global tc2_array
    global tc3_array
    global flow_array
    global power_array


    def __init__(self, widget):
        QMainWindow.__init__(self)

        #self.collection_task(widget)
        self.setWindowTitle("Benchmark Space Systems Resistojet Software")
        self.setCentralWidget(widget)

        #self.update_canvas()

        #self.timer = QtCore.QTimer()
        #self.timer.setInterval(50)
        #self.timer.timeout.connect(self.update_canvas)
        #self.timer.start()


    


        #self.update_plot(widget)

    def collection_task(self, widget):
        self.worker = worker()
        self.worker.started.connect(self.worker.run)
        self.worker.start()
        






if __name__ == "__main__":

    #setup()
    app = QApplication(sys.argv)
    widget = Widget()
    
    window = MainWindow(widget)
    window.resize(1000,900)



    window.show()
    sys.exit(app.exec())
