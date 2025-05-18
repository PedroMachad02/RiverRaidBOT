import cv2
import time
import numpy as np

from controls import Command
from elements import Player, Helicopter, Boat, Fuel, Passing

class Bot:
    def __init__(self, controls, auto_start=False):
        self.controls = controls
        self.player = Player()
        self.will_move = False
        self.enemies = []
        self.fuels = []
        self.passings = []
        self.started = auto_start
        self.start_time = time.time() 

    def refresh (self, frame):
        # Define Region Of Interest
        height, width = frame.shape[:2]
        y_start, y_end = 0, 480
        x_start, x_end = 0, width
        roi = frame[y_start:y_end, x_start:x_end]

        # Detect all entities in roi
        self.detect_player(roi)
        self.detect_objects(roi)
        self.detect_passings(roi)

        # Act based on entities
        self.action()

        # Clear all entities
        self.enemies = []
        self.fuels = []
        self.passings = []

    def fire (self):
        self.controls.input_commands([Command.B], hold=False)

    def move_to_element (self, element, avoid = False):
        print(element.name, avoid)
        direction = 1
        if avoid:
            direction = -1

        if self.will_move is False and self.player.x_diff(element) * direction > 0 and self.player.can_move_right:
            self.controls.input_commands([Command.RIGHT])
            self.will_move = True
        elif self.will_move is False and self.player.x_diff(element) * direction < 0 and self.player.can_move_left:
            self.controls.input_commands([Command.LEFT])
            self.will_move = True

    def action (self):
        self.will_move = False

        # Start game
        if not self.started and time.time() - self.start_time >= 3:
            self.controls.input_commands([Command.START])
            self.started = True
        elif not self.started:
            return

        # Handle enemies
        self.enemies.sort(key=lambda e: e.position[1], reverse=True)
        for enemy in self.enemies:
            if self.player.is_aiming(enemy):
                self.fire()
                self.move_to_element(enemy)
                break
            elif self.player.is_aligned(enemy, margin=3) and self.player.y_diff(enemy) > 40:
                self.fire()
                self.move_to_element(enemy)
                break
            elif self.player.is_aligned(enemy, margin=10) and self.player.y_diff(enemy) < 40:
                self.move_to_element(enemy, avoid=True)


        # Handle valid passings
        self.passings.sort(key=lambda p: abs(self.player.x_diff(p)))
        for passing in self.passings:
            if passing.includes(self.player):
                if abs(self.player.x_diff(passing)) > 20:
                    self.move_to_element(passing)
                    break
                else:
                    self.fuels.sort(key=lambda f: f.position[1], reverse=True)
                    for fuel in self.fuels:
                        if (self.player.is_aligned(fuel, margin=10) and not self.player.is_aiming(fuel)) or (self.player.y_diff(fuel) > 50 and abs(self.player.x_diff(fuel)) < 30):
                            self.move_to_element(fuel)
                            break
            elif passing.is_aligned(self.player):
                self.move_to_element(passing)
            else:
                self.move_to_element(passing)
            break

       
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

    def detect_player(self, frame):
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

            if 200 < area < 400 and 10 < w < 25:
                area_diff = abs(area - 300)
                if area_diff < best_area_diff:
                    best_match = (cnt, x + w // 2, y + h // 2)
                    best_area_diff = area_diff

        if best_match:
            cnt, center_x, center_y = best_match
            self.player.position = [center_x, center_y]
            cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
            self.player.present = True

            x, y = self.player.position
            cv2.circle(frame, self.player.position, radius=2, color=(0, 255, 0), thickness=-1)
            cv2.line(frame, [x-self.player.width//2, y], [x+self.player.width//2, y], color=(255, 0, 255), thickness=2)

            # Define green HSV range
            lower_blue = np.array([100, 100, 100])
            upper_blue = np.array([140, 255, 255])
            blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

            # Check left/right based on green presence
            x, y = self.player.position
            offset = self.player.width // 2 + 18

            frame_height, frame_width = frame.shape[:2]
            left_x = max(0, x - offset)
            right_x = min(frame_width - 1, x + offset)
            y = min(max(0, y), frame_height - 1) - 18

            # If pixel is NOT green, movement is allowed
            self.player.can_move_left = blue_mask[y, left_x] > 0
            self.player.can_move_right = blue_mask[y, right_x] > 0

            # Optional: draw indicators
            if self.player.can_move_left:
                cv2.circle(frame, (left_x, y), 3, (255, 255, 0), -1)  # Cyan
            else:
                cv2.circle(frame, (left_x, y), 3, (0, 0, 255), -1)    # Red (blocked)

            if self.player.can_move_right:
                cv2.circle(frame, (right_x, y), 3, (0, 255, 255), -1)  # Yellow
            else:
                cv2.circle(frame, (right_x, y), 3, (0, 0, 255), -1)    # Red (blocked)
        else:
            self.player.can_move_left = True
            self.player.can_move_right = True
            self.player.present = False

    def detect_passings(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        lower_gray = np.array([0, 0, 50])
        upper_gray = np.array([180, 50, 200])

        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        gray_mask = cv2.inRange(hsv, lower_gray, upper_gray)
        outside_mask = cv2.bitwise_or(green_mask, gray_mask)

        # Fill small holes in the green areas using morphological closing
        kernel = np.ones((20, 20), np.uint8) 
        closed_outside = cv2.morphologyEx(outside_mask, cv2.MORPH_CLOSE, kernel)

        # Row to analyze
        y = 270
        row = closed_outside[y]

        # Collect non-green segments
        self.passings = []
        start = None

        for x in range(len(row)):
            if row[x] == 0:  # Not green => part of line
                if start is None:
                    start = x
                cv2.circle(frame, (x, y), radius=1, color=(0, 255, 255), thickness=-1)  # Yellow dot
            else:
                if start is not None:
                    self.passings.append(Passing(start, x - 1))
                    start = None

        # If segment reaches the end
        if start is not None:
            self.passings.append(Passing(start, len(row) - 1))


