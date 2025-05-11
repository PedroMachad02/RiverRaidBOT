from cv2 import waitKey
from time import time

class Controls:

    KEY_MAP = {
        ord(' '): 0,    # B
        ord('2'): 1,    # 
        ord('1'): 2,    # Select
        ord('0'): 3,    # Start
        ord('w'): 4,    # Up
        ord('s'): 5,    # Down
        ord('a'): 6,    # Left
        ord('d'): 7,    # Right
        ord('c'): 8     # A
    }

    def __init__(self):
        self.pressed_keys = set()
        self.last_key_time = time()
        self.buttons = []
        self.clear_buttons()
        self.quit = False

    def clear_buttons(self):
        self.buttons = [0] * 9

    def input_buttons(self, input, ):
        print(input)
        self.clear_buttons()
        for key in input:
            if key in self.KEY_MAP:
                self.buttons[self.KEY_MAP[key]] = 1
                self.last_key_time = time()

    def update_buttons(self):
        if time() - self.last_key_time > 0.05:
            self.clear_buttons()

    def update_manual_buttons(self):
        self.update_buttons()

        self.input_buttons(self.pressed_keys)

        key = waitKey(1) & 0xFF
        if key != 255:
            self.pressed_keys.add(key)
            self.last_key_time = time()

        if key == ord('q'):
            self.quit = True

        return self.buttons
