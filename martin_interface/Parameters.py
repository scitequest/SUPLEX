# Used for individual spots and background rectangles.
# Depending on the type/shape of the Measure Field this either stores a position and diameter or coordinates.
# Further functions using Parameters have to be developed with this in mind.
class Parameters:
    def __init__(self, parameters):
        
        self._shape = parameters["type"]
        self._diameter = None
        self._coordinates = []
        self._position = None
        
        if "diameter" in parameters.keys():
            self._diameter = parameters["diameter"]
            
        if "position" in parameters.keys():
            self._position = Coordinate(parameters["position"][0], parameters["position"][1])
            
        if "coordinates" in parameters.keys():
            self._coordinates = []   
            for coord in parameters["coordinates"]:
                self.coordinates.append(Coordinate(coord[0], coord[1]))
        
    @property
    def shape(self):
        return self._shape
    
    @property
    def coordinates(self):
        return self._coordinates
    
    @property
    def diameter(self):
        return self._diameter
    
    @property
    def position(self):
        return self._position

class Coordinate:
    def __init__(self, x, y):
        self._x = x
        self._y = y
    
    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y