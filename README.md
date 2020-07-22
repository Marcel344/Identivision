# Identivision
Welcome to IdentiVision, a program uses your WebCam or a Tello Drone from DJI to guess the identity of a person using CNN, HOG and LBPH, all that in a clean PyQt5 user interface. LBPH models are saved locally and are loaded on start, CNN and HOG from face_recognition are computed at runtime via multiprocessing in order to avoid python's GIL. 
In order for this program to display reuslts, you need photos of people (at least 5 with visible faces) in the folder 'profilepics' with their names as the image name (Ex : Chad.jpg), For now the program only supports images of JPG type.


![Image of UI](https://github.com/Marcel344/Identivision/blob/master/identivision.png)

## Steps : 

1. pip3 install -r requirements.txt
2. connect drone (or if you want to use built in webcam then just press Use camera)
3. python3 main.py
