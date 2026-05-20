import math
import time
from adafruit_servokit import ServoKit

L1 = 26.5
L2 = 85.0
L3 = 154.0

COXA_OFFSET = -32.2

kit1 = ServoKit(channels=16, address=0x40)
kit2 = ServoKit(channels=16, address=0x41)

CHANNELS = {
    'L1': ((kit1, 1),  (kit1, 0),  (kit1, 2)),
    'L2': ((kit1, 4),  (kit1, 3),  (kit1, 5)),
    'L3': ((kit1, 7),  (kit1, 6),  (kit1, 8)),
    'R1': ((kit1, 10), (kit1, 9),  (kit1, 11)),
    'R2': ((kit1, 13), (kit1, 12), (kit1, 14)),
    'R3': ((kit2, 0),  (kit1, 15), (kit2, 1)),
}

RIGHT_LEGS = {'R1', 'R2', 'R3'}

def solve_ik(x, y, z):
    femur_offset = math.degrees(math.atan2(x, y))
    horiz = math.sqrt(x**2 + y**2) - L1
    reach = math.sqrt(horiz**2 + z**2)
    if reach > L2 + L3 or reach < abs(L2 - L3):
        return None
    phi = math.degrees(math.atan2(-z, horiz))
    cos_beta = max(-1, min(1, (L2**2 + reach**2 - L3**2) / (2 * L2 * reach)))
    beta = math.degrees(math.acos(cos_beta))
    coxa_offset = phi + beta - 90
    cos_gamma = max(-1, min(1, (L2**2 + L3**2 - reach**2) / (2 * L2 * L3)))
    gamma = math.degrees(math.acos(cos_gamma))
    tibia_offset = gamma - 90
    femur_servo = 90 + femur_offset
    coxa_servo  = 90 + coxa_offset + COXA_OFFSET
    tibia_servo = 90  # fixed while tuning
    if not all(0 <= a <= 180 for a in [femur_servo, coxa_servo, tibia_servo]):
        return None
    return (round(femur_servo, 1), round(coxa_servo, 1), round(tibia_servo, 1))

def set_leg(leg_name, x, y, z):
    channels = CHANNELS[leg_name]
    if leg_name in RIGHT_LEGS:
        x = -x
    angles = solve_ik(x, y, z)
    if angles is None:
        print(f"  {leg_name}: UNREACHABLE at ({x},{y},{z})")
        return
    f_ang, c_ang, t_ang = angles
    if leg_name in RIGHT_LEGS:
        # R coxa and femur: no flip needed
        pass
    else:
        # L coxa and femur: flip both
        f_ang = 180 - f_ang
        c_ang = 180 - c_ang
    f_kit, f_ch = channels[0]
    c_kit, c_ch = channels[1]
    t_kit, t_ch = channels[2]
    f_kit.servo[f_ch].angle = f_ang
    c_kit.servo[c_ch].angle = c_ang
    t_kit.servo[t_ch].angle = t_ang

def all_legs_neutral():
    print("Moving all legs to neutral standing position...")
    for leg in CHANNELS:
        set_leg(leg, 0, L1 + L2, -L3)
    time.sleep(1)

def all_legs_home():
    print("Moving all servos to 90 degrees home...")
    for ch in range(16):
        kit1.servo[ch].angle = 90
    kit2.servo[0].angle = 90
    kit2.servo[1].angle = 90
    time.sleep(1)

if __name__ == '__main__':
    print("Hexapod IK Test")
    print("L1=26.5mm  L2=85mm  L3=154mm\n")

    print("1. Homing all servos to 90 degrees...")
    all_legs_home()
    time.sleep(2)

    print("2. Moving to neutral standing position...")
    all_legs_neutral()
    time.sleep(2)

    print("3. Testing forward step on L1...")
    set_leg('L1', 50, L1 + L2, -L3)
    time.sleep(1)
    set_leg('L1', 0, L1 + L2, -L3)
    time.sleep(1)

    print("4. Testing lift on L1...")
    set_leg('L1', 0, L1 + L2, -80)
    time.sleep(1)
    set_leg('L1', 0, L1 + L2, -L3)
    time.sleep(1)

    print("5. Testing lift on R1...")
    set_leg('R1', 0, L1 + L2, -80)
    time.sleep(1)
    set_leg('R1', 0, L1 + L2, -L3)
    time.sleep(1)

    print("6. Testing all legs neutral...")
    all_legs_neutral()

    print("7. Testing all legs lift simultaneously...")
    for leg in CHANNELS:
        set_leg(leg, 0, L1 + L2, -80)
    time.sleep(2)
    all_legs_neutral()

    print("8. Testing tripod gait - group A lift (L1, R2, L3)...")
    for leg in ['L1', 'R2', 'L3']:
        set_leg(leg, 0, L1 + L2, -80)
    time.sleep(1)
    all_legs_neutral()
    time.sleep(1)

    print("9. Testing tripod gait - group B lift (R1, L2, R3)...")
    for leg in ['R1', 'L2', 'R3']:
        set_leg(leg, 0, L1 + L2, -80)
    time.sleep(1)
    all_legs_neutral()

    print("\nAll tests complete.")
