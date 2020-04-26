import face_recognition
import os
from multiprocessing import Process

class hogProcess(Process): 

    def __init__(self, algorithm_type, return_dict):
        self.MappedNames = []
        self.ModelNum = 0
        self.Algorithm = algorithm_type
        self.return_dict = return_dict
        super(hogProcess, self).__init__()

    def run(self):
        print("running...")
        known_faces = []

        counter = 0
        for filename in os.listdir(f'generated/{self.ModelNum}/faces'):

            # Load an image
            image = face_recognition.load_image_file(f'generated/{self.ModelNum}/faces/{filename}')

            # Get 128-dimension face encoding
            # Always returns a list of found faces, for this purpose we take first face only (assuming one face per image as you can't be twice on one image)
            encoding = face_recognition.face_encodings(image)

            # Append encodings and name
            counter = counter+1
            if encoding :
                known_faces.append(encoding)
            if len(known_faces)>5:
                break

        bestPrediction = 0
        predictedName = None
        for name in self.MappedNames:

            image = face_recognition.load_image_file(f'profilepics/{name}.jpg')

            # This time we first grab face locations - we'll need them to draw boxes
            locations = face_recognition.face_locations(image, model=self.Algorithm)

            # Now since we know loctions, we can pass them to face_encodings as second argument
            # Without that it will search for faces once again slowing down whole process
            encodings = face_recognition.face_encodings(image, locations)

            results = face_recognition.compare_faces(known_faces, encodings[0], 0.1)
            NbrOfTrueVals = self.getNumberOfTrueVals(results)
            if (bestPrediction < NbrOfTrueVals):
                bestPrediction = NbrOfTrueVals
                predictedName = name

        self.return_dict['Name'] = predictedName
            
    def setMappedNames (self, names):
        self.MappedNames = names
    
    def setModelNum (self, num):
        self.ModelNum = num
    
        
    def getNumberOfTrueVals (self, results):
        truths = 0
        for result in results:
            truths = truths + sum(result)
        return truths