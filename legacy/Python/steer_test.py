#!/bin/python3

import comms
import time
import sensor
import board
import digitalio
import threading
import pwmio
import math
import numpy as np
from adafruit_motor import servo
from typing import Tuple
from ast import literal_eval as l_eval



class Servo:
    left = 100
    neutral = 45
    right = 0

    def __init__(self, pwm=pwmio.PWMOut(board.D23, frequency=50)) -> None:
        self.s = servo.Servo(pwm, min_pulse=750, max_pulse=2250)

    def rotate(self, angle: int):
        self.s.angle = angle


def rotate_vector(pitch, roll, vector):
    pitch = math.radians(pitch)
    roll = math.radians(roll)
    x, y, z = vector

    rotated_x = x * math.cos(pitch) + y * math.sin(pitch)
    rotated_y = -x * math.sin(roll) * math.sin(pitch) + \
        y * math.cos(roll) + z * math.sin(roll)
    rotated_z = x * math.cos(roll) * math.sin(pitch) - \
        y * math.sin(roll) + z * math.cos(roll)

    return (rotated_x, rotated_y, rotated_z)


def calibrate_magnetometer(data, expected_ranges):
    """
    Calibrates a 3-axis magnetometer using two-point calibration.

    Args:
        data: A numpy array of shape (N, 3) containing magnetometer readings.
        expected_ranges: A numpy array of shape (3, 2) containing the expected range
                         (minimum and maximum values) for each axis in a known magnetic field.

    Returns:
        A numpy array of shape (N, 3) containing calibrated magnetometer readings.
    """
    # Calculate offsets for each axis
    offsets = (data.min(axis=0) + data.max(axis=0)) / 2

    # Subtract offsets from each reading on the corresponding axis
    data -= offsets

    # Calculate scaling factors for each axis
    ranges = data.max(axis=0) - data.min(axis=0)
    scaling_factors = expected_ranges[:, 1] - expected_ranges[:, 0]
    scaling_factors /= ranges

    # Multiply each corrected reading on the corresponding axis by the scaling factor
    data *= scaling_factors

    # Add offsets back to each reading on the corresponding axis
    data += offsets

    return data


def calculate_angles(acceleration_x, acceleration_y, acceleration_z):
    pitch = math.atan2(acceleration_x, math.sqrt(
        acceleration_y * acceleration_y + acceleration_z * acceleration_z))
    roll = math.atan2(acceleration_y, math.sqrt(
        acceleration_x * acceleration_x + acceleration_z * acceleration_z))
    pitch_degrees = math.degrees(pitch)
    roll_degrees = math.degrees(roll)
    return (pitch_degrees, roll_degrees)


def calibrate(magnetometer: sensor.adafruit_lis2mdl.LIS2MDL):
    # start_time = time.monotonic()
    hardiron_calibration = np.array(l_eval(open("cal_data").readline()))

    # # Calculate biases and scaling factors for the x-axis
    # bias_x = (hardiron_calibration[0][0] + hardiron_calibration[0][1]) / 2
    # scaling_factor_x = (
    #     hardiron_calibration[0][1] - hardiron_calibration[0][0]) / 2

    # # Calculate biases and scaling factors for the y-axis
    # bias_y = (hardiron_calibration[1][0] + hardiron_calibration[1][1]) / 2
    # scaling_factor_y = (
    #     hardiron_calibration[1][1] - hardiron_calibration[1][0]) / 2

    # # Calculate biases and scaling factors for the z-axis
    # bias_z = (hardiron_calibration[2][0] + hardiron_calibration[2][1]) / 2
    # scaling_factor_z = (
    #     hardiron_calibration[2][1] - hardiron_calibration[2][0]) / 2

    # # Assign biases to the offset property
    # magnetometer.offset = (bias_x, bias_y, bias_z)

    # # Assign scaling factors to the scale property
    # magnetometer.scale = (scaling_factor_x, scaling_factor_y, scaling_factor_z)

    return hardiron_calibration


def compass_reading(magnetometer_x, magnetometer_y, magnetometer_z):
    # Convert the magnetometer readings to radians
    # magnetometer_x_rad = math.radians(magnetometer_x)
    # magnetometer_y_rad = math.radians(magnetometer_y)
    
    # normvals = normalize(magvals, hardiron_calibration)
    # print("magnetometer: %s -> %s" % (magvals, normvals))

    # # we will only use X and Y for the compass calculations, so hold it level!
    # compass_heading = int(-math.atan2(normvals[2], normvals[1]) * 180.0 / math.pi)
    # raw_compass_heading = int(-math.atan2(magvals[2], magvals[1]) * 180.0 / math.pi)
    # # compass_heading is between -180 and +180 since atan2 returns -pi to +pi
    # # this translates it to be between 0 and 360
    # compass_heading += 450
    # compass_heading %= 360

    # Calculate the yaw angle in radians
    yaw = -math.atan2(magnetometer_z, magnetometer_y)

    # Convert the yaw angle to degrees
    yaw_degrees = math.degrees(yaw)

    # Normalize the compass reading to a range of 0-360 degrees
    compass_reading = (yaw_degrees + 450) % 360

    return compass_reading


def get_rotation(point1, point2):
    x1, y1 = point1
    x2, y2 = point2

    # Calculate the difference between the points
    dx = x2 - x1
    dy = y2 - y1

    # Calculate the angle from the positive x-axis
    angle = math.atan2(dy, dx)

    # Convert the angle from radians to degrees
    angle = math.degrees(angle)

    # Make sure the angle is positive
    if angle < 0:
        angle += 360

    return angle


def get_rotation_difference(current_heading, desired_heading):
    difference = desired_heading - current_heading
    if difference > 180:
        difference -= 360
    elif difference < -180:
        difference += 360
    return difference

def normalize(_magvals, hardiron_calibration):
    ret = [0, 0, 0]
    for i, axis in enumerate(_magvals):
        minv, maxv = hardiron_calibration[i]
        axis = min(max(minv, axis), maxv)  # keep within min/max calibration
        ret[i] = (axis - minv) * 200 / (maxv - minv) + -100
    return ret


def main():
    comms.SD_o = comms.SD("steering.log")
    SD_o = comms.SD_o
    sensor.SD_o = comms.SD_o
    sleeping = True
    last_rotate = time.time()
    e = 15
    desiredPos = (90, 21.040)
    bme = sensor.BME(i2c=board.I2C())
    lsm = sensor.LSM303()
    gps = sensor.L76x()
    
    hardiron_calibration = calibrate(lsm.mag)
    servo = Servo()

    while True:
        pitch, roll = calculate_angles(*lsm.getAcceleration())
        #
        if time.time() < last_rotate + 0.5:
            continue

        last_rotate = time.time()

        # mag_corected = rotate_vector(pitch, roll, lsm.getMagnetic())
        mag_corected = normalize(np.array(lsm.getMagnetic()), hardiron_calibration)
        compass = compass_reading(*mag_corected)
        # compass = compass_reading(*lsm.getMagnetic())
        rotation = get_rotation((52.218, 21.040), desiredPos)
        rotation_to_do = get_rotation_difference(compass, rotation)
        print(f"compass: {compass}, rotation: {rotation}, rotation_to_do: {rotation_to_do}")

        if rotation_to_do < -e:
            # go Left
            def repeat_function():
                servo.rotate(servo.left)
                start = time.monotonic()
                des_rotation = get_rotation(
                    (gps.getLat(), gps.getLon()), desiredPos)
                print('go left')
                while compass_reading(*rotate_vector(pitch, roll, lsm.getMagnetic())) < \
                        des_rotation - e and time.monotonic() < start + 2:
                    pass
                    # Add a delay if necessary
                    time.sleep(0.020)
                servo.rotate(servo.neutral)
                
        elif rotation_to_do > e:
            # go Right
            def repeat_function():
                servo.rotate(servo.right)
                start = time.monotonic()
                des_rotation = get_rotation(
                    (gps.getLat(), gps.getLon()), desiredPos)
                print('go right')
                while compass_reading(*rotate_vector(pitch, roll, lsm.getMagnetic())) > \
                        des_rotation + e and time.monotonic() < start + 2:
                    pass
                    # Add a delay if necessary
                    time.sleep(0.020)
                servo.rotate(servo.neutral)

        else:
            def repeat_function():
                servo.rotate(servo.neutral)
                pass

        repeat_function()

if __name__ == '__main__':
    main()
