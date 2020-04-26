
from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
import cv2
import os
import myModel
class cleanDataThread(QThread): 

    signal = pyqtSignal(str,name='PyQt_PyObject')
    modelsSignal = pyqtSignal('PyQt_PyObject')
    strLogSignal = pyqtSignal(str,name = "strLogSignal")
    removeSignal = pyqtSignal(str, name = "removeName")
    def __init__(self):
        self.MyModels = []
        self.MappedModels = []
        QThread.__init__(self)

    def run(self):
        photos = os.listdir("profilepics/")
        os.mkdir("profilepics/cleanData")
        foundFaces = []
        counter = 0
        size = len(photos)
        face_cascade = cv2.CascadeClassifier('/Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages/cv2/data/haarcascade_frontalface_alt2.xml')
        for photo in photos:
            counter = counter+1
            if(photo != '.DS_Store'):
                image = cv2.imread("profilepics/"+photo)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=10, minSize=(64,64),flags=cv2.CASCADE_SCALE_IMAGE)
                for (x, y, w, h) in faces:
                    cv2.imwrite("profilepics/cleanData/"+photo,gray[y: y + h, x: x + w])
                    foundFaces.append(photo)
            self.strLogSignal.emit(f"Looking for faces in profile pictures --- progress : {counter}/{size} - Found faces : {len(foundFaces)}")
        self.strLogSignal.emit(f"{len(foundFaces)} faces were found")


        trash = os.listdir("profilepics/")
        for face in trash :
            if not face in foundFaces:
                self.removeSignal.emit(os.path.splitext(face)[0])

        if(self.MyModels):
            for mModel in self.MyModels:
                if (not mModel.mappedNames):
                    bestPred = 100
                    faceName = ""
                    size = len(foundFaces)
                    counter = 0
                    for face in foundFaces:
                        counter = counter+1
                        self.strLogSignal.emit(f"Scanning profile photos for model {mModel.name} --- progress : {counter}/{size}")
                        prediction = mModel.model.predict(np.asarray(cv2.cvtColor(cv2.imread("profilepics/cleanData/"+face), cv2.COLOR_BGR2GRAY)))
                        confidence = prediction[1]
                        mModel.addName(os.path.splitext(face)[0], confidence)
                        if (confidence < bestPred):
                            bestPred = confidence
                            faceName = os.path.splitext(face)[0]
                    mModel.sortByConf()
                    self.MappedModels.append(mModel)
                else:
                    self.strLogSignal.emit(f"Model {mModel.name} already scanned, skipping")
                
                self.strLogSignal.emit("Done")
            


            self.modelsSignal.emit(self.MappedModels)

    def setModels(self, MyModels):
        self.MyModels = MyModels

    def addModel(self, model):
        self.MyModels.append(model)