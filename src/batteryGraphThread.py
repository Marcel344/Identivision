import re
import time
from PyQt5.QtCore import QThread, pyqtSignal

class batteryGraphThread(QThread):
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self, tello):
        self.tello = tello
        QThread.__init__(self)

    # run method gets called when we start the thread
    def run(self):  
        battery = 100
        counter = 0
        while battery>10:
            time.sleep(1)
            batterystr = self.tello.send_command_with_return("battery?")
            if batterystr:
                batterylist = [int(s) for s in re.findall(r'\b\d+\b', batterystr)]
                if len(batterylist)>0:
                    battery = batterylist[0]
                self.signal.emit(battery)