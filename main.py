import retro
import cv2
from time import sleep

# Define key-to-button index mapping
KEY_MAP = {
    ord(' '): 0,           # B
    ord('2'): 1,           # 
    ord('1'): 2,           # Select
    ord('0'): 3,           # Start
    ord('w'): 4,           # Up
    ord('s'): 5,           # Down
    ord('a'): 6,           # Left
    ord('d'): 7,           # Right
    ord('c'): 8            # A
}

# Initialize emulator from ROM file
jogo = retro.RetroEmulator("river-raid.a26")

# Initial empty button state
buttons = [0] * 9

while True:
    sleep(0.016)

    # Set current input state
    jogo.set_button_mask(buttons)

    # Advance one frame
    jogo.step()

    # Get the screen
    screen = jogo.get_screen()
    screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
    cv2.imshow("River Raid", screen)

    # Read key input
    key = cv2.waitKey(1) & 0xFF

    # If a key is pressed and mapped, toggle it
    if key in KEY_MAP:
        btn_index = KEY_MAP[key]
        buttons[btn_index] = 1  # Press

    # Release all buttons when no key is pressed (basic approach)
    else:
        buttons = [0] * 9

    if key == ord('q'):  # Quit with 'q'
        break

cv2.destroyAllWindows()
