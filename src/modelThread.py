
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import QtWidgets
import os
import time
import numpy as np
from PIL import Image
import cv2
class modelThread(QThread): # using LBPH (Local Binary Patterns Histograms Algorithm)
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self, modelsList):
        self.file = None
        self.model = None
        self.modelsList = modelsList
        QThread.__init__(self)

    def run(self):
        time.sleep(1)  
        if (self.file):
            print("\ntraining model ...")
            faces = [np.asarray(Image.open("generated/"+str(self.file)+"/faces/"+face)) for face in os.listdir("generated/"+str(self.file)+"/faces")]
            labels = [np.asarray(str(self.file)) for face in os.listdir("generated/"+str(self.file)+"/faces")]
            labels = np.asarray(labels, dtype=np.int32)
            model = cv2.face.LBPHFaceRecognizer_create(neighbors=8)
            model.train(faces, labels)
            model.save("generated/"+str(self.file)+"/model/model"+str(self.file)+".yaml")  
            self.modelsList.addItem(QtWidgets.QListWidgetItem("model"+str(self.file)))
            self.signal.emit(model)

    def setFile(self, file):
        self.file = file
