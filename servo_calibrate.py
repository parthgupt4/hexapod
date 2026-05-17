from adafruit_servokit import ServoKit
import time

kit = ServoKit(channels=16)

print("Servo Calibration Script")
print("Sending 90 degrees to each servo one at a time")
print("Press Enter to move to next servo, Ctrl+C to quit\n")

servo_labels = [
    "L1_coxa", "L1_femur", "L1_tibia",
    "L2_coxa", "L2_femur", "L2_tibia",
    "L3_coxa", "L3_femur", "L3_tibia",
    "R1_coxa", "R1_femur", "R1_tibia",
    "R2_coxa", "R2_femur", "R2_tibia",
    "R3_coxa", "R3_femur", "R3_tibia",
]

for i, label in enumerate(servo_labels):
    input(f"Press Enter to calibrate channel {i} ({label})...")
    kit.servo[i].angle = 90
    print(f"  → {label} set to 90°. Attach horn now if not attached.")
    time.sleep(0.5)

print("\nAll servos calibrated!")
