"""
Move all servos to neutral (90 deg) so the hexapod stands still.

Run: python3 stand.py

The PCA9685 holds the last commanded PWM after this script exits, so the
servos stay in position as long as power is connected.
"""

from tripod_direct import neutral

if __name__ == '__main__':
    neutral()
    print("Standing at neutral. Servos hold until power is cut.")
