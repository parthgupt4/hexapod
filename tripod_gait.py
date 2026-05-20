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

LEG_ANGLES = {
    'L1':  45, 'L2':  90, 'L3': 135,
    'R1': -45, 'R2': -90, 'R3': -135,
}

GROUP_A = ['L1', 'R2', 'L3']
GROUP_B = ['R1', 'L2', 'R3']

STEP_HEIGHT = 40
STEP_LENGTH = 60
NEUTRAL_Y   = L1 + L2
NEUTRAL_Z   = -L3
PHASE_TIME  = 0.4  # slower = more traction

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
    femur_servo = 90 + femur_offset
    coxa_servo  = 90 + coxa_offset + COXA_OFFSET
    tibia_servo = 90
    if not all(0 <= a <= 180 for a in [femur_servo, coxa_servo, tibia_servo]):
        return None
    return (round(femur_servo, 1), round(coxa_servo, 1), round(tibia_servo, 1))

def set_leg(leg_name, x, y, z):
    channels = CHANNELS[leg_name]
    if leg_name in RIGHT_LEGS:
        x = -x
    angles = solve_ik(x, y, z)
    if angles is None:
        return
    f_ang, c_ang, t_ang = angles
    if leg_name not in RIGHT_LEGS:
        f_ang = 180 - f_ang
        c_ang = 180 - c_ang
    f_kit, f_ch = channels[0]
    c_kit, c_ch = channels[1]
    t_kit, t_ch = channels[2]
    f_kit.servo[f_ch].angle = f_ang
    c_kit.servo[c_ch].angle = c_ang
    t_kit.servo[t_ch].angle = t_ang

def leg_forward_x(leg_name, dx):
    """Convert world forward dx to leg local x using mounting angle."""
    angle_rad = math.radians(LEG_ANGLES[leg_name])
    return dx * math.cos(angle_rad)

def all_legs_neutral():
    for leg in CHANNELS:
        set_leg(leg, 0, NEUTRAL_Y, NEUTRAL_Z)

def all_legs_home():
    for ch in range(16):
        kit1.servo[ch].angle = 90
    kit2.servo[0].angle = 90
    kit2.servo[1].angle = 90

def tripod_step(step_length=STEP_LENGTH):
    """
    Full tripod gait cycle:
    - Group A lifts and swings forward
    - Group B pushes body forward (stays on ground, moves backward)
    - Group A plants
    - Group B lifts and swings forward
    - Group A pushes body forward
    - Group B plants
    """

    # Phase 1: Group A lift and swing forward
    for leg in GROUP_A:
        lx = leg_forward_x(leg, step_length)
        set_leg(leg, lx, NEUTRAL_Y, NEUTRAL_Z + STEP_HEIGHT)
    time.sleep(PHASE_TIME * 0.3)

    # Phase 2: Group B push back (moves body forward), Group A plant
    for leg in GROUP_A:
        lx = leg_forward_x(leg, step_length)
        set_leg(leg, lx, NEUTRAL_Y, NEUTRAL_Z)
    for leg in GROUP_B:
        lx = leg_forward_x(leg, -step_length)
        set_leg(leg, lx, NEUTRAL_Y, NEUTRAL_Z)
    time.sleep(PHASE_TIME)

    # Phase 3: Group B lift and swing forward
    for leg in GROUP_B:
        lx = leg_forward_x(leg, step_length)
        set_leg(leg, lx, NEUTRAL_Y, NEUTRAL_Z + STEP_HEIGHT)
    time.sleep(PHASE_TIME * 0.3)

    # Phase 4: Group A push back, Group B plant
    for leg in GROUP_B:
        lx = leg_forward_x(leg, step_length)
        set_leg(leg, lx, NEUTRAL_Y, NEUTRAL_Z)
    for leg in GROUP_A:
        lx = leg_forward_x(leg, -step_length)
        set_leg(leg, lx, NEUTRAL_Y, NEUTRAL_Z)
    time.sleep(PHASE_TIME)

    # Reset to neutral
    all_legs_neutral()
    time.sleep(PHASE_TIME * 0.3)

if __name__ == '__main__':
    print("Tripod Gait Test - place on carpet")
    print("Homing...")
    all_legs_home()
    time.sleep(2)

    print("Neutral position...")
    all_legs_neutral()
    time.sleep(2)

    print("Walking forward 5 steps...")
    for i in range(5):
        print(f"  Step {i+1}...")
        tripod_step()

    print("Done. Returning to neutral...")
    all_legs_neutral()
