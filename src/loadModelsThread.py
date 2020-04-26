
from PyQt5.QtCore import QThread, pyqtSignal
import myModel
from os import path
import cv2
class loadModelsThread(QThread): # using LBPH (Local Binary Patterns Histograms Algorithm)
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        QThread.__init__(self)

    def run(self):
        models = []
        counter = 0
        while(path.isdir("generated/"+str(counter)+"/model")):
            model = cv2.face.LBPHFaceRecognizer_create()
            cv2.face_FaceRecognizer.read(model,"generated/"+str(counter)+"/model/model"+str(counter)+".yaml")
            newModel = myModel.myModel(model, str(counter))
            models.append(newModel)
            counter = counter+1
        print(models)
        self.signal.emit(models)

