# Identivision
Welcome to IdentiVision, a program uses your WebCam or a Tello Drone from DJI to guess the identity of a person using CNN, HOG and LBPH, all that in a clean PyQt5 user interface. LBPH models are saved locally and are loaded on start, CNN and HOG from face_recognition are computed at runtime via multiprocessing in order to avoi python's GIL. 
In order for this program to display reuslts, you need photos of people (at least 5 with visible faces) in the folder 'profilepics' with their names as the image name (Ex : Chad.jpg), For now the program only supports images of JPG type.
