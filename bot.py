import cv2
import time
import numpy as np

from controls import Command

class Bot:
    def __init__(self, controls):
        self.controls = controls
        self.player = Player()
        self.enemies = []
        self.fuels = []
        self.started = False
        self.running = False
        self.start_time = time.time() 

    def refresh (self, frame):
        height, width = frame.shape[:2]
        y_start, y_end = 0, 480
        x_start, x_end = 0, width
        roi = frame[y_start:y_end, x_start:x_end]

        self.player.identify(roi)
        self.detect_objects(roi)

        self.action()

        self.enemies = []
        self.fuels = []

    def action (self):
        if not self.started and time.time() - self.start_time >= 3:
            self.controls.input_commands([Command.START])
            self.started = True
            return
        elif not self.started:
            return
        elif not self.running and self.player.present:
            self.controls.input_commands([Command.B])
            self.running = True
            return
        elif not self.running:
            return

        for enemy in self.enemies:
            if self.player.is_aligned(enemy):
                self.controls.input_commands([Command.B])
                return

        for fuel in self.fuels:
            if self.player.is_aligned(fuel):
                self.controls.input_commands([Command.B])
                return

       
    def detect_objects(self, frame):
        frame = frame.copy()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define color ranges for objects in HSV
        color_ranges = {
            "ENEMY": {
                "color": [(50, 100, 50), (90, 255, 255)], # Green-ish
                "area": [50,53]
            },     
            "FUEL":  { 
                "color": [(0, 100, 100), (5, 255, 255)], # Red-ish (fuel top and bottom)
                "area": [229, 229]
            },    
            "BOAT": {
                "color": [(0, 180, 150), (10, 255, 255)],  # Red middle of boat
                "area": [200, 250]
            }
        }

        for label, data in color_ranges.items():
            lower, upper = data["color"]
            area_min, area_max = data["area"]

            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                area = cv2.contourArea(cnt)
                
                if area > 30 and area_min <= area <= area_max:
                    x, y, w, h = cv2.boundingRect(cnt)
                    position = [x + w // 2, y + h // 2]

                    cv2.drawContours(frame, [cnt], -1, (255, 255, 255), 1)
                    cv2.putText(frame, f"{label}, {w}, {h}, {area}", (x, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

                    if label == "ENEMY":
                        self.enemies.append(Helicopter(position))
                    elif label == "FUEL":
                        self.fuels.append(Fuel(position))
                    elif label == "BOAT":
                        self.enemies.append(Boat(position))


        for enemy in self.enemies:            
            width = enemy.width
            x, y = enemy.position
            cv2.circle(frame, position, radius=2, color=(0, 255, 0), thickness=-1)
            cv2.line(frame, [x-width//2, y], [x+width//2, y], color=(255, 0, 255), thickness=2)

        for fuel in self.fuels:
            width = fuel.width
            x, y = fuel.position
            cv2.circle(frame, position, radius=2, color=(0, 255, 0), thickness=-1)
            cv2.line(frame, [x-width//2, y], [x+width//2, y], color=(255, 0, 255), thickness=2)

        cv2.imshow("Detected Objects", frame)


class Element:
    def __init__(self, name, position, width):
        self.name = name
        self._position = position
        self.width = width
        self.left = position[0] - width // 2
        self.right = position[0] + width // 2

    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, value):
        self._position = value
        self.left = self._position[0] - self.width // 2
        self.right = self._position[0] + self.width // 2
    
    def is_aligned(self, element):
        return self.left <= element.left <= self.right or self.left <= element.right <= self.right


class Player (Element):
    def __init__(self, position = [0, 0]):
        super().__init__("Player", position, 20)
        self.position = position
        self.present = False


    def identify(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_yellow = (20, 100, 100)
        upper_yellow = (30, 255, 255)
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_match = None
        best_area_diff = float("inf")

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)

            if 260 < area < 400 and 15 < w < 25:
                area_diff = abs(area - 300)
                if area_diff < best_area_diff:
                    best_match = (cnt, x + w // 2, y + h // 2)
                    best_area_diff = area_diff

        if best_match:
            cnt, center_x, center_y = best_match
            self.position = [center_x, center_y]
            cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
            self.present = True
        else:
            self.present = False

        x, y = self.position
        cv2.circle(frame, self.position, radius=2, color=(0, 255, 0), thickness=-1)
        cv2.line(frame, [x-self.width//2, y], [x+self.width//2, y], color=(255, 0, 255), thickness=2)

        cv2.imshow("Plane", frame)


class Enemy (Element):
    def __init__(self, name, position, width):
        super().__init__(name, position, width)

class Helicopter (Enemy):
    def __init__(self, position):
        x, y = position
        super().__init__("Helicopter", [x-5, y], width=30)

class Boat (Enemy):
    def __init__(self, position):
        x, y = position
        super().__init__("Boat", [x, y], width=50)

class Fuel (Element):
    def __init__(self, position):
        super().__init__("Fuel", position, width=20)

    