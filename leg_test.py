from adafruit_servokit import ServoKit
import time

kit = ServoKit(channels=16)

joints = {
    'L1_coxa': 0, 'L1_femur': 1, 'L1_tibia': 2,
    'L2_coxa': 3, 'L2_femur': 4, 'L2_tibia': 5,
    'L3_coxa': 6, 'L3_femur': 7, 'L3_tibia': 8,
    'R1_coxa': 9, 'R1_femur': 10, 'R1_tibia': 11,
    'R2_coxa': 12, 'R2_femur': 13, 'R2_tibia': 14,
    'R3_coxa': 15,
}

print("Setting all servos to 90 degrees neutral position")
for name, ch in joints.items():
    kit.servo[ch].angle = 90
time.sleep(2)

print("\nTesting each joint one at a time...")
for name, ch in joints.items():
    input(f"\nPress Enter to test {name} (channel {ch})...")
    print(f"  Moving to 60 degrees...")
    kit.servo[ch].angle = 60
    time.sleep(1)
    print(f"  Moving to 120 degrees...")
    kit.servo[ch].angle = 120
    time.sleep(1)
    print(f"  Back to 90 degrees...")
    kit.servo[ch].angle = 90
    time.sleep(0.5)
    print(f"  {name} done. Note which direction it moved.")

print("\nAll joints tested!")
