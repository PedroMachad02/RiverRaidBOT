import retro
import cv2
import time
import os
import argparse

from bot import Bot
from controls import Controls

def parse_args():
    parser = argparse.ArgumentParser(description="River Raid Bot Controller")
    parser.add_argument(
        "--rom", type=str, default="river-raid.a26",
        help="Path to the game ROM file (default: river-raid.a26)"
    )
    parser.add_argument(
        "--state", type=str,
        help="Path to the saved state file (default: states/saved_state.bin)"
    )
    parser.add_argument(
        "--fps", type=int, default=60,
        help="Game FPS"
    )
    return parser.parse_args()

def load_state(game, path):
    if path is None or not os.path.exists(path):
        print("No saved state.")
        return False
    
    with open(path, "rb") as f:
        game.set_state(f.read())
    print("State loaded.")
    return True


def save_state(game, path):
    with open(path, "wb") as f:
        f.write(game.get_state())


def get_frame(game):
    CROP_TOP = 6
    CROP_BOTTOM = 602
    CROP_LEFT = 24
    CROP_RIGHT = 480

    frame = game.get_screen()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # Convert the screen to BGR format
    scaled_frame = cv2.resize(frame, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST) # Resize the screen for better visibility
    real_frame = scaled_frame[CROP_TOP:CROP_BOTTOM, CROP_LEFT:CROP_RIGHT]
    return real_frame
    


def main ():
    args = parse_args()

    # Initialize game and bot
    game = retro.RetroEmulator(args.rom)
    game_load = load_state(game, args.state)
    controls = Controls()
    bot = Bot(controls, auto_start=game_load)

    while True:
        # Frame Start
        start_time = time.perf_counter()
        key = cv2.waitKey(1)

        # Display game and refresh bot state
        frame = get_frame(game)
        cv2.imshow("River Raid", frame)
        bot.refresh(frame)

        # Update controls + manual input
        controls.update_inputs()
        controls.process_key(key)
        game.set_button_mask(controls.buttons)
        if controls.save:
            save_state(game, args.state)
            controls.save = False
        if controls.quit:
            break

        # Game FPS management
        game.step()
        elapsed = time.perf_counter() - start_time
        time.sleep(max(0, 1/args.fps - elapsed))


    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
