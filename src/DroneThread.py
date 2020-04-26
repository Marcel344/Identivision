
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import QtGui
from PyQt5 import Qt
from djitellopy import Tello
import cv2
import numpy as np
import time

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

class DroneThread(QThread):

    pixSignal = pyqtSignal(Qt.QPixmap,name = "pixSignal") 

    upSignal = pyqtSignal(int,name = "upSignal")
    downSignal = pyqtSignal(int,name = "downSignal")
    leftSignal = pyqtSignal(int,name = "leftSignal")
    rightSignal = pyqtSignal(int,name = "rightSignal")


    def __init__(self):
        self.tello = Tello()
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        QThread.__init__(self)

    def run(self):
        self.tello.send_command_without_return("command")
        self.tello.streamon()
        while self.tello.stream_on:
            frame_read = self.tello.get_frame_read()
             # setting Face Box properties
            fbCol = (255, 0, 0) #BGR 0-255 
            fbStroke = 2
            

            frameRet = frame_read.frame
            frameRet  = cv2.cvtColor(frameRet, cv2.COLOR_BGR2RGB)
            faces = face_cascade.detectMultiScale(frameRet, scaleFactor=1.5, minNeighbors=2)

             # Target size
            tSize = faceSizes[3]

            # These are our center dimensions
            cWidth = int(dimensions[0]/2)
            cHeight = int(dimensions[1]/2)

            # end coords are the end of the bounding box x & y

            for (x, y, w, h) in faces:

                end_cord_x = x + w
                end_cord_y = y + h
                end_size = w*2

                # these are our target coordinates
                targ_cord_x = int((end_cord_x + x)/2)
                targ_cord_y = int((end_cord_y + y)/2) + UDOffset

                # Draw the face bounding box
                cv2.rectangle(frameRet, (x, y), (end_cord_x, end_cord_y), fbCol, fbStroke)

                # Draw the target as a circle
                cv2.circle(frameRet, (targ_cord_x, targ_cord_y), 10, (0,255,0), 2)

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

            img = QtGui.QImage(frameRet, frameRet.shape[1], frameRet.shape[0], QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap.fromImage(img)
            self.pixSignal.emit(pix)
            self.rightSignal.emit(0)
            self.upSignal.emit(0)
            self.downSignal.emit(0)
            self.leftSignal.emit(0)
            self.update()
            self.updateCoordsTxt()
            vid = self.tello.get_video_capture()
            time.sleep(1/60)
    

    def update(self):
        """ Update routine. Send velocities to Tello."""
        self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity, self.up_down_velocity,
                                       self.yaw_velocity)

    def updateCoordsTxt(self):
        if self.left_right_velocity > 0:
            self.rightSignal.emit(self.left_right_velocity)

        if self.left_right_velocity < 0:
            self.leftSignal.emit(self.left_right_velocity)

        if self.up_down_velocity > 0:
            self.upSignal.emit(self.up_down_velocity)

        if self.up_down_velocity < 0:
            self.downSignal.emit(self.up_down_velocity)

    def get_drone(self):
        return self.tello