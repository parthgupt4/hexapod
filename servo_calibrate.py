from adafruit_servokit import ServoKit
import time

kit = ServoKit(channels=16)

print("Servo Calibration Script")
print("Plug each servo into channel 0, press Enter to move to 90 degrees")
print("Script will HOLD position until you confirm horn is attached\n")

servo_labels = [
    "L1_coxa", "L1_femur", "L1_tibia",
    "L2_coxa", "L2_femur", "L2_tibia",
    "L3_coxa", "L3_femur", "L3_tibia",
    "R1_coxa", "R1_femur", "R1_tibia",
    "R2_coxa", "R2_femur", "R2_tibia",
    "R3_coxa", "R3_femur", "R3_tibia",
]

for i, label in enumerate(servo_labels):
    input(f"[{i+1}/18] Plug in {label} to channel 0, then press Enter...")
    kit.servo[0].angle = 90
    print(f"  → Holding at 90°. Attach horn now.")
    input(f"  → Press Enter when horn is attached and screwed in...")
    kit.servo[0].angle = None
    print(f"  → {label} done. Unplug it.\n")

print("All 18 servos calibrated!")

