import retro
import cv2
import time
import os

from bot import Bot
from controls import Controls


def get_frame(game):
    frame = game.get_screen()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # Convert the screen to BGR format
    scaled_frame = cv2.resize(frame, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST) # Resize the screen for better visibility
    real_frame = scaled_frame[6:602,24:480] # Crop the screen to remove unnecessary borders
    return real_frame


def display_screen(title, frame):
    cv2.imshow(title, frame)


def main ():
    game = retro.RetroEmulator("river-raid.a26")

    state_path = "states/saved_state.bin"
    game_load = False
    if os.path.exists(state_path):
        with open(state_path, "rb") as f:
            game.set_state(f.read())
        game_load = True
        print("State loaded.")
    else:
        print("No saved state found.")

    controls = Controls()
    bot = Bot(controls, auto_start=game_load)

    while True:
        key = cv2.waitKey(1)

        frame = get_frame(game)
        display_screen("River Raid", frame)
        bot.refresh(frame)

        controls.process_key(key)
        controls.update_inputs()
        game.set_button_mask(controls.buttons)
        if controls.save:
            with open(state_path, "wb") as f:
                f.write(game.get_state())
            controls.save = False
        if controls.quit:
            break

        game.step()
        time.sleep(0.016) # Set the frame rate (60 FPS)


    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
