"""
Controller mode for the hexapod.

Reads USB gamepad input (js0) and dispatches motions from tripod_direct.
A background thread pumps gamepad events into shared state; the main loop
reads that state and runs the matching motion. This keeps inputs responsive
even though each gait step takes ~0.8 s.

Install on the Pi:
    pip3 install inputs --break-system-packages

Run:
    python3 controller.py
"""

import threading
import time

from inputs import get_gamepad, UnpluggedError

from tripod_direct import (
    neutral,
    squat,
    step_backward,
    step_forward,
    turn_left,
    turn_right,
)

# This controller reports axes as 0..255 unsigned with 128 at rest.
AXIS_CENTER = 128.0
AXIS_HALF_RANGE = 128.0
# Fraction of full deflection required before a direction registers.
DEADZONE = 0.4

# Many controllers report stick-up as a negative Y. Flip if forward/back is inverted.
Y_FORWARD_SIGN = -1

state = {
    'x': 0.0,
    'y': 0.0,
    'squat_requested': False,
    'stop': False,
}
state_lock = threading.Lock()


# Set to True to print every controller event — use this to discover the
# correct axis codes and value range for your controller.
DEBUG_PRINT_EVENTS = False


def gamepad_reader():
    while True:
        try:
            events = get_gamepad()
        except UnpluggedError:
            print("Controller unplugged.")
            with state_lock:
                state['stop'] = True
            return

        for event in events:
            if DEBUG_PRINT_EVENTS and event.ev_type in ('Absolute', 'Key'):
                print(f"  event: type={event.ev_type} code={event.code} state={event.state}")
            if event.ev_type == 'Absolute':
                if event.code == 'ABS_X':
                    with state_lock:
                        state['x'] = (event.state - AXIS_CENTER) / AXIS_HALF_RANGE
                elif event.code == 'ABS_Y':
                    with state_lock:
                        state['y'] = ((event.state - AXIS_CENTER) / AXIS_HALF_RANGE) * Y_FORWARD_SIGN
            elif event.ev_type == 'Key' and event.code == 'BTN_SOUTH':
                if event.state == 1:
                    with state_lock:
                        state['squat_requested'] = True


def main():
    print("Controller mode. Left stick = move/turn, A/cross = squat. Ctrl-C to quit.")
    neutral()

    threading.Thread(target=gamepad_reader, daemon=True).start()

    try:
        while True:
            with state_lock:
                if state['stop']:
                    break
                x = state['x']
                y = state['y']
                do_squat = state['squat_requested']
                state['squat_requested'] = False

            if do_squat:
                print("Squat")
                squat(reps=1, down_delay=0.15, up_delay=0.15)
                continue

            if abs(y) > DEADZONE and abs(y) >= abs(x):
                if y > 0:
                    print("Forward")
                    step_forward()
                else:
                    print("Backward")
                    step_backward()
            elif abs(x) > DEADZONE:
                if x < 0:
                    print("Turn left")
                    turn_left()
                else:
                    print("Turn right")
                    turn_right()
            else:
                time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        neutral()
        print("Returned to neutral.")


if __name__ == '__main__':
    main()
