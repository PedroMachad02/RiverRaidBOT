import retro
import cv2
from time import sleep


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


def init_game():
    jogo = retro.RetroEmulator("river-raid.a26")
    return jogo


def get_frame(jogo):
    frame = jogo.get_screen()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # Convert the screen to BGR format
    scaled_frame = cv2.resize(frame, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST) # Resize the screen for better visibility
    return scaled_frame


def display_screen(title, frame):
    cv2.imshow(title, frame)


def main ():
    jogo = init_game()
    buttons = [0] * 9

    while True:
        sleep(0.016) # Set the frame rate (60 FPS)

        jogo.set_button_mask(buttons)

        jogo.step()
        frame = get_frame(jogo)
        display_screen("River Raid", frame)

        key = cv2.waitKey(1) & 0xFF
        if key in KEY_MAP:
            btn_index = KEY_MAP[key]
            buttons[btn_index] = 1  # Press
        else:
            buttons = [0] * 9

        if key == ord('q'): # Quit with 'q'
            break  

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
