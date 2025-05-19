class Element:
    def __init__(self, name, position, width, present=True):
        self.name = name
        self._position = position
        self.width = width
        self.left = position[0] - width // 2
        self.right = position[0] + width // 2
        self.present = present

    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, value):
        self._position = value
        self.left = self._position[0] - self.width // 2
        self.right = self._position[0] + self.width // 2
    
    def is_aligned(self, element, margin = 0, tolerance = 0):
        selfLeft = self.left - margin
        selfRight = self.right + margin
        elementLeft = element.left + tolerance
        elementRight = element.right - tolerance
        return selfLeft <= elementLeft <= selfRight or selfLeft <= elementRight <= selfRight
    
    def x_diff(self, element):
        return element.position[0] - self.position[0]
    
    def y_diff(self, element):
        return self.position[1] - element.position[1]


class Player (Element):
    color = [(20, 100, 100), (30, 255, 255)]
    area = [200, 400] 

    def __init__(self, position = [0, 0]):
        super().__init__("Player", position, 20, present=(position != [0,0]))
        self.position = position
        self.can_move_left = True
        self.can_move_right = True

    def is_aiming (self, element, tolerance = 2):
        selfCenter = self.position[0]
        elementCenter = element.position[0]
        elementLeft = elementCenter - tolerance
        elementRight = elementCenter + tolerance
        return elementLeft <= selfCenter <= elementRight


class Enemy (Element):
    def __init__(self, name, position, width):
        super().__init__(name, position, width)
        


class Helicopter (Enemy):
    color = [(50, 100, 50), (90, 255, 255)] # Dark Green
    area = [50, 53]

    def __init__(self, position):
        x, y = position
        super().__init__("Helicopter", [x-2, y], width=30)

class Boat (Enemy):
    color = [(0, 180, 150), (10, 255, 255)] # Dark Red
    area = [200, 250]

    def __init__(self, position):
        super().__init__("Boat", position, width=50)

class Plane (Enemy):
    color = [(100, 50, 100), (140, 150, 255)] # Light Blue
    area = [120, 130]

    def __init__(self, position):
        super().__init__("Plane", position, width=25)


class Fuel (Element):
    color = [(0, 100, 100), (5, 255, 255)] # Light Red
    area = [229, 229]

    def __init__(self, position):
        super().__init__("Fuel", position, width=20)


class Passing (Element):
    def __init__(self, start, end):
        super().__init__("Passing", [(end + start) // 2, 10], end - start)
    
    def includes (self, element):
        return self.left <= element.left and self.right >= element.right