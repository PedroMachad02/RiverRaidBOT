import retro
import cv2
import time

from bot import Bot
from controls import Controls


def init_game():
    jogo = retro.RetroEmulator("river-raid.a26")
    return jogo


def get_frame(jogo):
    frame = jogo.get_screen()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # Convert the screen to BGR format
    scaled_frame = cv2.resize(frame, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST) # Resize the screen for better visibility
    real_frame = scaled_frame[6:602,24:480] # Crop the screen to remove unnecessary borders
    return real_frame


def display_screen(title, frame):
    cv2.imshow(title, frame)


def main ():
    jogo = init_game()

    controls = Controls()
    bot = Bot(controls)

    while True:
        key = cv2.waitKey(1)

        frame = get_frame(jogo)
        bot.refresh(frame)
        display_screen("River Raid", frame)

        controls.process_key(key)
        controls.update_inputs()
        jogo.set_button_mask(controls.buttons)
        if controls.quit:
            break

        jogo.step()
        time.sleep(0.016) # Set the frame rate (60 FPS)


    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
