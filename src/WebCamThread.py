
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import QtGui
from PyQt5 import Qt
import cv2
import numpy as np
import time
from os import path
import os
import myModel
import modelThread

# Speed of the drone
S = 15
S2 = 7

# These are the values in which kicks in speed up mode, as of now, this hasn't been finalized or fine tuned so be careful
# Tested are 3, 4, 5
acc = [500, 250, 250, 150, 110, 70, 50]

UDOffset = 150
dimensions = (960, 720)
faceSizes = [1026, 684, 456, 304, 202, 136, 90]
face_cascade = cv2.CascadeClassifier('/Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages/cv2/data/haarcascade_frontalface_alt2.xml')

class WebCamThread(QThread):

    pixSignal = pyqtSignal(Qt.QPixmap,name = "pixSignal")
    strLogSignal = pyqtSignal(str,name = "strLogSignal")
    currentModelSignal = pyqtSignal('PyQt_PyObject')
    newModelSignal = pyqtSignal('PyQt_PyObject')
    ProgressBarSignal = pyqtSignal(int, name = "ProgressBarSignal")

    upSignal = pyqtSignal(int,name = "upSignal")
    downSignal = pyqtSignal(int,name = "downSignal")
    leftSignal = pyqtSignal(int,name = "leftSignal")
    rightSignal = pyqtSignal(int,name = "rightSignal")

    
    def __init__(self, modelsList):
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.modelThread = modelThread.modelThread(modelsList)
        self.modelThread.signal.connect(self.setModel)
        self.folder = 0
        self.models = []
        self.timeWithNewFace = 0
        self.isRunning = False


        folder = 0 
        if (path.isdir('generated')):
            newModel = cv2.face.LBPHFaceRecognizer_create()
            cv2.face_FaceRecognizer.read(newModel,"generated/"+str(folder)+"/model/model"+str(folder)+".yaml")
            self.myModel = myModel.myModel(newModel, str(folder))

        else:
            self.myModel = None

        self.file = None
        QThread.__init__(self)

    def setModel(self, model):
        self.strLogSignal.emit("model generated")
        self.myModel = myModel.myModel(model,str(self.folder))
        self.newModelSignal.emit(self.myModel)
        self.models.append(self.myModel)


    def setModels(self, models):
        self.models = models
        if self.models :
            self.myModel = models[0] #to update the name of the model that is currently being used


    def setNumOfModels (self, num):
        self.folder = num

    def getFile(self):
        return self.file

    def run(self):
        while(self.isRunning):
            vc = cv2.VideoCapture(0)
            rval, frame = vc.read()
            self.file = None
            pics = 0
            frameCounter = 0
                
            if (not path.isdir('generated')):
                os.mkdir("generated")
                os.mkdir("generated/"+str(self.folder))
                os.mkdir("generated/"+str(self.folder)+"/faces")
                os.mkdir("generated/"+str(self.folder)+"/model")
            else :
                self.strLogSignal.emit("using existing models !")


            while rval:

                rval, frameRet = vc.read()

                # setting Face Box properties
                fbCol = (91, 209, 80) #BGR 0-255 
                fbStroke = 2
                
                frameRect  = cv2.cvtColor(frameRet, cv2.COLOR_BGR2RGB)
                faces = face_cascade.detectMultiScale(frameRect, scaleFactor=1.2, minNeighbors=10, minSize=(64,64),flags=cv2.CASCADE_SCALE_IMAGE)



                # Target size
                tSize = faceSizes[1]

                # These are our center dimensions
                cWidth = int(dimensions[0]/2)
                cHeight = int(dimensions[1]/2)

                # end coords are the end of the bounding box x & y

                isface = False
                for (x, y, w, h) in faces:

                    end_cord_x = x + w
                    end_cord_y = y + h
                    end_size = w*2
                    isface = True

                    # these are our target coordinates
                    targ_cord_x = int((end_cord_x + x)/2)
                    targ_cord_y = int((end_cord_y + y)/2) + UDOffset

                    # Draw the face bounding box
                    cv2.rectangle(frameRect, (x, y), (end_cord_x, end_cord_y), fbCol, fbStroke)
                    if self.myModel :
                        if self.myModel.mappedNames :
                            cv2.putText(frameRect,self.myModel.mappedNames[0][0], (int(x+(end_cord_x-x)/3), end_cord_y+35), cv2.FONT_HERSHEY_COMPLEX, 1, (208,255,124), 2)


                    # This calculates the vector from your face to the center of the screen
                    vTrue = np.array((cWidth ,cHeight ,tSize))
                    vTarget = np.array((targ_cord_x ,targ_cord_y ,end_size))
                    vDistance = vTrue-vTarget

                    if vDistance[0] < -100:
                        self.yaw_velocity = S
                        self.left_right_velocity = S2
                    elif vDistance[0] > 100:
                        self.yaw_velocity = -S
                        self.left_right_velocity = -S2
                    else:
                        self.yaw_velocity = 0
                    
                    # for up & down
                    if vDistance[1] > 100:
                        self.up_down_velocity = S
                    elif vDistance[1] < -100:
                        self.up_down_velocity = -S
                    else:
                        self.up_down_velocity = 0

                    F = 0
                    if abs(vDistance[2]) > acc[3]:
                        F = S

                    # for forward back
                    if vDistance[2] > 0:
                        self.for_back_velocity = S + F
                    elif vDistance[2] < 0:
                        self.for_back_velocity = -S - F
                    else:
                        self.for_back_velocity = 0

                img = QtGui.QImage(frameRect, frameRect.shape[1], frameRect.shape[0], QtGui.QImage.Format_RGB888)
                pix = QtGui.QPixmap.fromImage(img)
                self.pixSignal.emit(pix)
                self.rightSignal.emit(0)
                self.upSignal.emit(0)
                self.downSignal.emit(0)
                self.leftSignal.emit(0)
                self.updateCoordsTxt()

                if (pics<100 and self.myModel == None and isface): # new face has been detected
                    frameCounter = frameCounter+3
                    if(frameCounter > 1):
                        if (not path.isdir('generated/'+str(self.folder))):
                            os.mkdir("generated/"+str(self.folder))
                            os.mkdir("generated/"+str(self.folder)+"/faces")
                            os.mkdir("generated/"+str(self.folder)+"/model")
                        frameCounter = 0
                        name = "generated/"+str(self.folder)+"/faces/"+"/%d.jpg"%pics
                        face = cv2.cvtColor(frameRet, cv2.COLOR_BGR2GRAY)
                        cv2.imwrite(name,face[y: y + h, x: x + w])
                        self.ProgressBarSignal.emit(pics+1)
                        self.strLogSignal.emit("Fetching frames from new face --- progress : %d"%(pics+1)+"/100 ")
                        pics = pics+1
                
                if(pics == 100 and self.myModel == None):
                    pics=101 #frames already saved, we only need to enter this block once
                    self.file = self.folder
                    self.modelThread.setFile(str(self.folder))
                    self.modelThread.start()
                    self.strLogSignal.emit("generating new model ...")

                if(self.myModel and isface):
                    prediction = self.myModel.model.predict(np.asarray(cv2.cvtColor(frameRet[y: y + h, x: x + w],cv2.COLOR_BGR2GRAY)))
                    if(prediction[1] > 30):
                        bestModel, newPrediction = self.getLowestModelPrediction(frameRet[y: y + h, x: x + w])
                        self.timeWithNewFace = self.timeWithNewFace + 1
                        if (newPrediction>30 and self.timeWithNewFace > 60): # aka 60 frames have passed with a new face (just making sure there is no model that fits the face)
                            self.strLogSignal.emit(str(prediction))
                            self.strLogSignal.emit("no models match, generating new model ...")
                            self.myModel = None 
                            self.folder = self.folder+1
                            self.timeWithNewFace = 0
                            pics = 0
                        
                        else :
                            self.myModel = bestModel
                            if self.timeWithNewFace == 1 :
                                self.currentModelSignal.emit(self.myModel)
                            self.strLogSignal.emit("searching in existing models")
                            self.strLogSignal.emit(str(prediction))

                    else:
                        self.timeWithNewFace = 0
                        self.strLogSignal.emit(str(prediction))
                time.sleep(1/60)

    def getLowestModelPrediction(self, frame):
        lowestConfidence = 120
        bestModel = None
        
        for mymodel in self.models :
            prediction = mymodel.model.predict(np.asarray(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)))
            self.strLogSignal.emit("model : "+str(prediction[0])+" conf : "+str(prediction[1]))
            if(prediction[1] < lowestConfidence):
                lowestConfidence = prediction[1]
                bestModel = mymodel
        return bestModel, lowestConfidence

    def updateName (self):
        self.currentModelSignal.emit(self.myModel)

    def updateCoordsTxt(self):
        if self.left_right_velocity > 0:
            self.rightSignal.emit(self.left_right_velocity)

        if self.left_right_velocity < 0:
            self.leftSignal.emit(self.left_right_velocity)

        if self.up_down_velocity > 0:
            self.upSignal.emit(self.up_down_velocity)

        if self.up_down_velocity < 0:
            self.downSignal.emit(self.up_down_velocity)
