from math import nan
import cv2
import time
import numpy as np

from controls import Command
from elements import Bridge, Player, Helicopter, Boat, Plane, Fuel, Passing

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
        enemies, self.fuels = self.detect_objects(roi)
        self.enemies = self.keep_same(self.enemies, enemies)
        self.detect_passings(roi)
        cv2.imshow("Detected Objects", roi)

        # Act based on entities
        self.action()

        # Clear entities
        self.fuels = []
        self.passings = []

    def fire (self):
        if self.controls.manual:
            return
        self.controls.input_commands([Command.B], hold=False)

    def move_to_element (self, element, avoid = False):
        direction = 1
        if avoid:
            direction = -1

        if self.controls.manual:
            return
        if element.name == "Plane":
            return
        
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
            if enemy.name == "Plane":
                if enemy.predicted_x_at_y0 is not nan and abs(self.player.position[0] - enemy.predicted_x_at_y0) < 70:
                    self.controls.input_commands([Command.UP])
            if self.player.is_aiming(enemy, tolerance=5) or (enemy.name == "Bridge" and self.player.is_aligned(enemy, margin=50)):
                fuel_ahead = False
                for fuel in self.fuels:
                    if self.player.is_aligned(fuel) and fuel.position[1] > enemy.position[1]:
                        fuel_ahead = True
                if not fuel_ahead:
                    self.fire()
                    self.move_to_element(enemy)
                    break
            elif self.player.is_aligned(enemy, margin=5) and self.player.y_diff(enemy) > 50:
                self.move_to_element(enemy)
            elif self.player.is_aligned(enemy, margin=25) and self.player.y_diff(enemy) < 50:
                self.move_to_element(enemy, avoid=True)

        # Handle valid passings considering fuels
        near_fuels = [fuel for fuel in self.fuels if self.player.is_aligned(fuel, margin=35)]
        near_fuels.sort(key=lambda f: f.position[1], reverse=True)
        self.passings.sort(key=lambda p: abs(self.player.x_diff(p)))
        for passing in self.passings:
            if passing.includes(self.player):
                if (abs(self.player.x_diff(passing)) > 50 and len(near_fuels) > 0) or (abs(self.player.x_diff(passing)) > 15 and len(near_fuels) == 0):
                    self.move_to_element(passing)
            else:
                self.move_to_element(passing)
            break

        # Handle fuels
        for fuel in near_fuels:
            self.move_to_element(fuel)
            break

       
    def detect_objects(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        enemies = []
        fuels = []

        # Define objects to be identified
        object_classes = [Helicopter, Plane, Boat, Fuel, Bridge]
        objects = [cls([0,0]) for cls in object_classes]

        for object in objects: # Detect all shapes that match the color mask
            lower, upper = object.color
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                area = cv2.contourArea(cnt)
                area_min, area_max = object.area

                if area > 30 and area_min <= area <= area_max: # Validate shape using area and create instance
                    cv2.drawContours(frame, [cnt], -1, (255, 255, 255), 1) # Draw object rectangle
                    x, y, w, h = cv2.boundingRect(cnt)
                    position = [x + w // 2, y + h // 2]
                    if isinstance(object, Helicopter):
                        enemies.append(Helicopter(position))
                    elif isinstance(object, Fuel):
                        fuels.append(Fuel(position))
                    elif isinstance(object, Boat):
                        enemies.append(Boat(position))
                    elif isinstance(object, Plane):
                        enemies.append(Plane(position))
                    elif isinstance(object, Bridge):
                        enemies.append(Bridge(position))

        # Draw object identification
        all_objects = (x for lst in (enemies, fuels) for x in lst)
        for object in all_objects:            
            x, y = object.position
            cv2.putText(frame, f"{object.name}", (x, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            cv2.circle(frame, position, radius=2, color=(0, 255, 0), thickness=-1)
            cv2.line(frame, [object.left, y], [object.right, y], color=(255, 0, 255), thickness=2)

        return enemies, fuels


    def detect_player(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower, upper = self.player.color
        mask = cv2.inRange(hsv, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_match = None
        best_area_diff = float("inf")

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)
            area_min, area_max = self.player.area
            w_min = self.player.width - 5
            w_max = self.player.width + 5

            if area_min <= area <= area_max and w_min <= w <= w_max:
                area_diff = abs(area - ((area_max - area_min) / 2))
                if area_diff < best_area_diff:
                    best_match = (cnt, x + w // 2, y + h // 2)
                    best_area_diff = area_diff

        if best_match:
            cnt, center_x, center_y = best_match
            self.player.position = [center_x, center_y]
            self.player.present = True
            

            x, y = self.player.position
            cv2.circle(frame, [x, y], radius=1, color=(0, 255, 0), thickness=1)
            cv2.line(frame, [self.player.left, y], [self.player.right, y], color=(255, 0, 255), thickness=2)

            # Define movement limits
            lower_blue = np.array([100, 100, 100])
            upper_blue = np.array([140, 255, 255])
            blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

            # Check left/right based on green presence
            x, y = self.player.position
            offset = self.player.width // 2 + 18
            second_offset = 30

            frame_height, frame_width = frame.shape[:2]
            left_x = max(0, x - offset)
            right_x = min(frame_width - 1, x + offset)
            y = min(max(0, y), frame_height - 1) - 18

            # If pixel is blue, movement is allowed
            self.player.can_move_left = blue_mask[y, left_x] > 0 and blue_mask[y + second_offset, left_x] > 0
            self.player.can_move_right = blue_mask[y, right_x] > 0 and blue_mask[y + second_offset, right_x] > 0

            # Draw indicators
            if self.player.can_move_left:
                cv2.circle(frame, (left_x, y), 3, (255, 255, 0), -1)
                cv2.circle(frame, (left_x, y + second_offset), 3, (255, 255, 0), -1)
            else:
                cv2.circle(frame, (left_x, y), 3, (0, 0, 255), -1)  
                cv2.circle(frame, (left_x, y + second_offset), 3, (0, 0, 255), -1)  
            if self.player.can_move_right:
                cv2.circle(frame, (right_x, y), 3, (255, 255, 0), -1)  
                cv2.circle(frame, (right_x, y + second_offset), 3, (255, 255, 0), -1)  
            else:
                cv2.circle(frame, (right_x, y), 3, (0, 0, 255), -1)  
                cv2.circle(frame, (right_x, y + second_offset), 3, (0, 0, 255), -1)  
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
            if row[x] == 0:  # Part of the passing
                if start is None:
                    start = x
                cv2.circle(frame, (x, y), radius=1, color=(0, 255, 255), thickness=1)
            else:
                if start is not None:
                    self.passings.append(Passing(start, x - 1))
                    start = None

        # If segment reaches the end
        if start is not None:
            self.passings.append(Passing(start, len(row) - 1))

    def keep_same(self, old, new):
        result = []
        for new_item in new:
            match = next((old_item for old_item in old if old_item.is_same(new_item)), None)
            if match:
                match.position = new_item.position
            result.append(match if match else new_item)
        return result

