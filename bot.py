import cv2
import time

class Bot:
    def __init__(self, controls):
        self.player = Player()
        self.controls = controls
        self.enemies = []
        self.started = False
        self.running = False
        self.start_time = time.time() 

    def refresh (self, frame):
        self.player.identify(frame)
        self.controls.update_buttons()
        self.get_input_buttons()

    def get_input_buttons (self):
        if not self.started and time.time() - self.start_time >= 3:
            self.controls.input_buttons([ord('0')])
            self.started = True
        elif not self.running and self.player.present:
            self.controls.input_buttons([ord(' ')])
            self.running = True
       
    # def identify_enemies (self, frame):
    #     height, width = frame.shape[:2]
    #     y_start, y_end = 420, 480
    #     x_start, x_end = 0, width
    #     roi = frame[y_start:y_end, x_start:x_end]

    #     hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    #     lower_red = (0, 100, 100)
    #     upper_red = (10, 255, 255)
    #     red_mask = cv2.inRange(hsv, lower_red, upper_red)

    #     contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #     for cnt in contours:
    #         x, y, w, h = cv2.boundingRect(cnt)
    #         area = cv2.contourArea(cnt)

    #         if area > 300:
    #             enemy_position = [x + w // 2, y + h // 2]
    #             self.enemies.append(Enemy(enemy_position))
    #             cv2.drawContours(roi, [cnt], -1, (0, 0, 255), 2)


class Element:
    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.present = False


class Player (Element):
    def __init__(self, position = [0, 0]):
        super().__init__("Player", position)
        self.position = position

    def identify(self, frame):
        height, width = frame.shape[:2]
        y_start, y_end = 420, 480
        x_start, x_end = 0, width
        roi = frame[y_start:y_end, x_start:x_end]

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
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
            cv2.drawContours(roi, [cnt], -1, (0, 255, 0), 2)
            self.present = True
        else:
            self.present = False

        # Show the result
        cv2.imshow("Plane", roi)


# class Enemy (Element):
#     def __init__(self, position):
#         super().__init__("Enemy", position = [0, 0])
#         self.position = position

    