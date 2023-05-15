# SPDX-FileCopyrightText: 2019 Mikey Sklar for Adafruit Industries
#
# SPDX-License-Identifier: MIT


from multiprocessing import Process, Queue, Value, Array
import time
import board
import digitalio
import math
import sys
import haversine

sys.path.append('..')

from Can.sensor import LSM303


def normalize(_magvals, hardiron_calibration):
    ret = [0, 0, 0]
    for i, axis in enumerate(_magvals):
        minv, maxv = hardiron_calibration[i]
        axis = min(max(minv, axis), maxv)  # keep within min/max calibration
        ret[i] = (axis - minv) * 200 / (maxv - minv) + -100
    return ret


def compass_reading(magnetometer_x, magnetometer_y, magnetometer_z):

    yaw = -math.atan2(magnetometer_y, magnetometer_x)

    # Convert the yaw angle to degrees
    # yaw_degrees = math.degrees(yaw)

    # Normalize the compass reading to a range of 0-360 degrees
    # compass_reading = (yaw_degrees + 450) % 360

    return yaw


def calc_pitch(_x, _y, _z):
    # assumes that x is forward y is right and z is down
    # angle between z axis and vector of acceleratrion
    return math.atan2(_x, _z)
    

class Stepper:
    reverse = False

    def __init__(self, steps_per_circle=200*108/19, delay=1,
                 en=digitalio.DigitalInOut(board.D18),
                 step_pin=digitalio.DigitalInOut(board.D4),
                 dir_pin=digitalio.DigitalInOut(board.D17)
                 ) -> None:
        self.delay = delay
        self.steps = steps_per_circle

        self.enable_pin = en
        self.step_pin = step_pin
        self.dir_pin = dir_pin

        self.enable_pin.direction = digitalio.Direction.OUTPUT
        self.step_pin.direction = digitalio.Direction.OUTPUT
        self.dir_pin.direction = digitalio.Direction.OUTPUT

        self.enable_pin.value = False

    def step_to_rad(self, steps):
        return steps * math.pi * 2 / self.steps

    def rad_to_step(self, angle):
        return self.steps * angle // (2 * math.pi)

    def rotate(self, angle, degrees=False):

        if degrees:
            angle = math.radians(angle)

        steps_to_do = self.steps * angle // (2 * math.pi)

        if self.reverse:
            steps_to_do *= -1

        if steps_to_do > 0:
            self.forward(steps_to_do)

        elif steps_to_do < 0:
            self.backwards(steps_to_do)

    def forward(self, steps):
        self.dir_pin.value = 0
        delay = self.delay
        for _ in range(steps):
            self.step_pin.value = 1
            time.sleep(delay)
            self.step_pin.value = 0
            time.sleep(delay)

    def backwards(self, steps):
        self.dir_pin.value = 1
        delay = self.delay
        for _ in range(steps):
            self.step_pin.value = 1
            time.sleep(delay)
            self.step_pin.value = 0
            time.sleep(delay)


class StepperH:
    reverse = False

    def __init__(self, steps_per_circle=200, delay=1,
                 en=digitalio.DigitalInOut(board.D18),
                 A1=digitalio.DigitalInOut(board.D4),
                 A2=digitalio.DigitalInOut(board.D17),
                 B1=digitalio.DigitalInOut(board.D23),
                 B2=digitalio.DigitalInOut(board.D24)) -> None:
        self.delay = delay
        self.steps = steps_per_circle

        self.enable_pin = en
        self.coil_A_1_pin = A1
        self.coil_A_2_pin = A2
        self.coil_B_1_pin = B1
        self.coil_B_2_pin = B2

        self.enable_pin.direction = digitalio.Direction.OUTPUT
        self.coil_A_1_pin.direction = digitalio.Direction.OUTPUT
        self.coil_A_2_pin.direction = digitalio.Direction.OUTPUT
        self.coil_B_1_pin.direction = digitalio.Direction.OUTPUT
        self.coil_B_2_pin.direction = digitalio.Direction.OUTPUT

        self.enable_pin.value = True

    def rotate(self, angle, degrees=False):
        if degrees:
            angle = math.radians(angle)
        steps_to_do = self.steps * angle // 2 * math.pi

        if self.reverse:
            steps_to_do *= -1

        if steps_to_do > 0:
            self.forward(steps_to_do)

        elif steps_to_do < 0:
            self.backwards(steps_to_do)

    def forward(self, steps):
        i = 0
        delay = self.delay
        while i in range(0, steps):
            self.setStep(1, 0, 1, 0)
            time.sleep(delay)
            self.setStep(0, 1, 1, 0)
            time.sleep(delay)
            self.setStep(0, 1, 0, 1)
            time.sleep(delay)
            self.setStep(1, 0, 0, 1)
            time.sleep(delay)
            i += 1

    def backwards(self, steps):
        i = 0
        delay = self.delay
        while i in range(0, steps):
            self.setStep(1, 0, 0, 1)
            time.sleep(delay)
            self.setStep(0, 1, 0, 1)
            time.sleep(delay)
            self.setStep(0, 1, 1, 0)
            time.sleep(delay)
            self.setStep(1, 0, 1, 0)
            time.sleep(delay)
            i += 1

    def setStep(self, w1, w2, w3, w4):
        self.coil_A_1_pin.value = w1
        self.coil_A_2_pin.value = w2
        self.coil_B_1_pin.value = w3
        self.coil_B_2_pin.value = w4


class Aimbot:
    target_pos = Array('d', [90, 0])
    self_pos = (0, 0)
    h_rot = Value('d',0)
    v_rot = Value('d',0)
    alt_diff = Value('d', 0)
    h_motor = Stepper()
    v_motor = Stepper()
    lsm: LSM303

    def calibrate(self):
        self.hardiron_calibration = [[0, 0], [0, 0], [0, 0]]
        steps_per_pass = int(self.h_motor.steps)
        v_passes = 4
        for p in range(v_passes):

            if p % 2:
                mf = self.h_motor.forward
            else:
                mf = self.h_motor.backwards

            for _ in range(steps_per_pass):
                mf(1)
                magval = self.lsm.magcals
                # print("Calibrating - X:{0:10.2f}, Y:{1:10.2f}, Z:{2:10.2f} uT".format(*magval))
                for i, axis in enumerate(magval):
                    self.hardiron_calibration[i][0] = min(
                        self.hardiron_calibration[i][0], axis)
                    self.hardiron_calibration[i][1] = max(
                        self.hardiron_calibration[i][1], axis)
            self.v_motor.rotate(math.pi/18)
        for _ in range(v_passes):
            self.v_motor.rotate(-math.pi/18)

    def __init__(self, pos, h_motor=Stepper(), v_motor=Stepper(), lsm=LSM303()):
        self.h_motor = h_motor
        self.v_motor = v_motor
        self.self_pos = pos
        self.calibrate()
        self.tracker = Process(target=self.track)
        self.tracker.start()
        self.lsm = lsm

    @staticmethod
    def calc_antenna_angle(ant_pos, goal_pos, goal_alt, degrees=True):
        """Calculate angles for antenna rotation  to goal pointreturn angles alfa and beta
        alfa - angle of rotation horizontally from north
        beta - angle of rotation vertically 

        ant_pos - gps position of antenna
        goal_pos - gps position of point to aim at
        goal_alt - altitude (in meters) of goal point above antenna
        """

        alfa = math.atan2(goal_pos[1] - ant_pos[1], goal_pos[0] - ant_pos[0])

        dist = haversine.haversine_distance(
            ant_pos, goal_pos, haversine.Unit.METERS)
        beta = math.atan2(goal_alt, dist)

        if degrees:
            return math.degrees(alfa), math.degrees(beta)
        else:
            return alfa, beta

    def track(self):
        h_step_angle = self.h_motor.step_to_rad(1)
        v_step_angle = self.v_motor.step_to_rad(1)
        while True:
            alfa, beta = self.calc_antenna_angle(self.self_pos, self.target_pos[:], self.alt_diff.value, degrees=False)
            heading = compass_reading(*normalize(self.lsm.getMagnetic(), self.hardiron_calibration))
            pitch = calc_pitch(*self.lsm.getAcceleration())
            h_rot = alfa - heading
            if h_rot - h_step_angle > 0:
                self.h_motor.forward(1)
            elif h_rot + h_step_angle < 0:
                self.h_motor.backwards(1)
            
            v_rot = beta - pitch
            if v_rot - v_step_angle > 0:
                self.v_motor.forward(1)
            elif v_rot + v_step_angle < 0:
                self.v_motor.backwards(1)  
            
            

while __name__ == '__main__':
    user_delay = input("Delay between steps (milliseconds)?")
    user_steps = input("How many steps forward? ")
    stepper = Stepper()
    stepper.delay = int(user_delay)
    stepper.forward(int(user_steps))
    user_steps = input("How many steps backwards? ")
    stepper.backwards(int(user_steps))