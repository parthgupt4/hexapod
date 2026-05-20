import time
from adafruit_servokit import ServoKit

kit1 = ServoKit(channels=16, address=0x40)
kit2 = ServoKit(channels=16, address=0x41)

# Channel map: femur, coxa, tibia
CH = {
    'L1': (1,  0,  2),
    'L2': (4,  3,  5),
    'L3': (7,  6,  8),
    'R1': (10, 9,  11),
    'R2': (13, 12, 14),
    'R3': (0,  15, 1),  # kit2 for femur and tibia
}

GROUP_A = ['L1', 'R2', 'L3']
GROUP_B = ['R1', 'L2', 'R3']

NEUTRAL_FEMUR = 90
NEUTRAL_COXA  = 90
NEUTRAL_TIBIA = 90

# How far forward/back legs swing (split per side to correct drift)
L_SWING = 44
R_SWING = 30
# How high legs lift
LIFT  = 25

def set_servo(leg, femur, coxa, tibia):
    f_ch, c_ch, t_ch = CH[leg]
    if leg in ['R1', 'R2', 'R3']:
        kit = kit1
        if leg == 'R3':
            kit2.servo[f_ch].angle = femur
            kit1.servo[c_ch].angle = coxa
            kit2.servo[t_ch].angle = tibia
            return
        kit1.servo[f_ch].angle = femur
        kit1.servo[c_ch].angle = coxa
        kit1.servo[t_ch].angle = tibia
    else:
        kit1.servo[f_ch].angle = femur
        kit1.servo[c_ch].angle = coxa
        kit1.servo[t_ch].angle = tibia

def neutral():
    for leg in CH:
        set_servo(leg, NEUTRAL_FEMUR, NEUTRAL_COXA, NEUTRAL_TIBIA)

def home():
    for ch in range(16):
        kit1.servo[ch].angle = 90
    kit2.servo[0].angle = 90
    kit2.servo[1].angle = 90

def step_forward():
    """
    Left legs: femur > 90 = back, femur < 90 = forward
    Right legs: femur < 90 = back, femur > 90 = forward
    Coxa < 90 = up for left, coxa > 90 = up for right... 
    we'll test directions below
    """
    # Phase 1: Lift group A, swing forward
    # Left legs in A (L1, L3): femur to 90-L_SWING = forward
    # Right legs in A (R2): femur to 90+R_SWING = forward
    # Coxa up: left=90-LIFT, right=90+LIFT
    set_servo('L1', 90-L_SWING, 90-LIFT, 90)
    set_servo('R2', 90+R_SWING, 90+LIFT, 90)
    set_servo('L3', 90-L_SWING, 90-LIFT, 90)
    # Group B stays on ground, push back
    set_servo('R1', 90-R_SWING, 90, 90)
    set_servo('L2', 90+L_SWING, 90, 90)
    set_servo('R3', 90-R_SWING, 90, 90)
    time.sleep(0.3)

    # Phase 2: Plant group A
    set_servo('L1', 90-L_SWING, 90, 90)
    set_servo('R2', 90+R_SWING, 90, 90)
    set_servo('L3', 90-L_SWING, 90, 90)
    time.sleep(0.1)

    # Phase 3: Lift group B, swing forward
    set_servo('R1', 90+R_SWING, 90+LIFT, 90)
    set_servo('L2', 90-L_SWING, 90-LIFT, 90)
    set_servo('R3', 90+R_SWING, 90+LIFT, 90)
    # Group A push back
    set_servo('L1', 90+L_SWING, 90, 90)
    set_servo('R2', 90-R_SWING, 90, 90)
    set_servo('L3', 90+L_SWING, 90, 90)
    time.sleep(0.3)

    # Phase 4: Plant group B
    set_servo('R1', 90+R_SWING, 90, 90)
    set_servo('L2', 90-L_SWING, 90, 90)
    set_servo('R3', 90+R_SWING, 90, 90)
    time.sleep(0.1)

    neutral()
    time.sleep(0.1)

if __name__ == '__main__':
    print("Direct servo tripod gait test")
    home()
    time.sleep(2)
    neutral()
    time.sleep(2)

    print("Walking 5 steps...")
    for i in range(5):
        print(f"Step {i+1}")
        step_forward()

    neutral()
    print("Done")

