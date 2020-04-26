
class myModel:
    model =  None
    name = None
    mappedNames = [()]

    def __init__ (self, model, name):
        self.model = model
        self.name = name
        self.mappedNames = []
    
    def addName (self, name, conf):
        self.mappedNames.append((name,conf))
    
    def sortByConf (self):
        self.mappedNames.sort(key=self.conf)

    def conf (self, element):
        return element[1]
