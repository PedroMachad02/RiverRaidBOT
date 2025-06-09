from time import time
from enum import Enum

class Command(Enum):
    B = 0
    UNKNOWN = 1
    SELECT = 2
    START = 3
    UP = 4
    DOWN = 5
    LEFT = 6
    RIGHT = 7
    A = 8

KEY_MAP = {
    ord(' '): Command.B,
    ord('2'): Command.UNKNOWN,
    ord('1'): Command.SELECT,
    ord('0'): Command.START,
    ord('w'): Command.UP,
    ord('s'): Command.DOWN,
    ord('a'): Command.LEFT,
    ord('d'): Command.RIGHT,
    ord('c'): Command.A
}

class Input():
    def __init__(self, command):
        self.command = command
        self.time = time()

class Controls:
    def __init__(self):
        self.inputs = []
        self.buttons = [0] * 9
        self.quit = False
        self.save = False
        self.manual = False

    def clear_buttons(self):
        self.buttons = [0] * 9  
        self.inputs = []    

    def input_commands(self, commands, hold=True):
        for i, command in enumerate(commands):
            if hold is True:
                self.inputs = [inp for inp in self.inputs if inp.command != command]

            if hold is True or self.buttons[command.value] == 0:
                self.inputs.append(Input(command))
                self.buttons[command.value] = 1

    def update_inputs(self):        
        for input in self.inputs:
            if time() - input.time > 0.001:
                self.buttons[input.command.value] = 0
                self.inputs.pop(0)
            else:
                break

    def process_key(self, key):
        if key != 255 and key in KEY_MAP:
            self.clear_buttons()
            self.input_commands([KEY_MAP[key]])

        if key == ord('q'):
            self.quit = True
        
        if key == ord('p'):
            self.save = True

        if key == ord('m'):
            self.manual = not self.manual
