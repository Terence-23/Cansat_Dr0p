#!/bin/python3
from typing import Tuple
import comms, sensor
import time
import board, digitalio
import threading
import pwmio

from adafruit_motor import servo


class Servo:
    left = 100
    neutral = 45
    right = 0

    def __init__(self, pwm = pwmio.PWMOut(board.D23, frequency=50)) -> None:
        self.s = servo.Servo(pwm, min_pulse=750, max_pulse=2250)

    def rotate(self, angle:int):
        self.s.angle = angle

import math



def rotate_vector(pitch, roll, vector):
    pitch = math.radians(pitch)
    roll = math.radians(roll)
    x, y, z = vector

    rotated_x = x * math.cos(pitch) + y * math.sin(pitch)
    rotated_y = -x * math.sin(roll) * math.sin(pitch) + y * math.cos(roll) + z * math.sin(roll)
    rotated_z = x * math.cos(roll) * math.sin(pitch) - y * math.sin(roll) + z * math.cos(roll)

    return (rotated_x, rotated_y, rotated_z)


def calculate_angles(acceleration_x, acceleration_y, acceleration_z):
    pitch = math.atan2(acceleration_x, math.sqrt(acceleration_y * acceleration_y + acceleration_z * acceleration_z))
    roll = math.atan2(acceleration_y, math.sqrt(acceleration_x * acceleration_x + acceleration_z * acceleration_z))
    pitch_degrees = math.degrees(pitch)
    roll_degrees = math.degrees(roll)
    return (pitch_degrees, roll_degrees)


def calibrate(magnetometer:sensor.adafruit_lis2mdl.LIS2MDL):
    start_time = time.monotonic()
    hardiron_calibration = [[1000, -1000], [1000, -1000], [1000, -1000]]

    # Update the high and low extremes
    while time.monotonic() - start_time < 10.0:
        magval = magnetometer.magnetic
        print("Calibrating - X:{0:10.2f}, Y:{1:10.2f}, Z:{2:10.2f} uT".format(*magval))
        for i, axis in enumerate(magval):
            hardiron_calibration[i][0] = min(hardiron_calibration[i][0], axis)
            hardiron_calibration[i][1] = max(hardiron_calibration[i][1], axis)
    print("Calibration complete:")
    print("hardiron_calibration =", hardiron_calibration)

    # Calculate biases and scaling factors for the x-axis
    bias_x = (hardiron_calibration[0][0] + hardiron_calibration[0][1]) / 2
    scaling_factor_x = (hardiron_calibration[0][1] - hardiron_calibration[0][0]) / 2

    # Calculate biases and scaling factors for the y-axis
    bias_y = (hardiron_calibration[1][0] + hardiron_calibration[1][1]) / 2
    scaling_factor_y = (hardiron_calibration[1][1] - hardiron_calibration[1][0]) / 2

    # Calculate biases and scaling factors for the z-axis
    bias_z = (hardiron_calibration[2][0] + hardiron_calibration[2][1]) / 2
    scaling_factor_z = (hardiron_calibration[2][1] - hardiron_calibration[2][0]) / 2

    # Assign biases to the offset property
    magnetometer.offset = (bias_x, bias_y, bias_z)

    # Assign scaling factors to the scale property
    magnetometer.scale = (scaling_factor_x, scaling_factor_y, scaling_factor_z)

    return magnetometer


def compass_reading(magnetometer_x, magnetometer_y, _=None):
    # Convert the magnetometer readings to radians
    magnetometer_x_rad = math.radians(magnetometer_x)
    magnetometer_y_rad = math.radians(magnetometer_y)
    
    # Calculate the yaw angle in radians
    yaw = math.atan2(magnetometer_y_rad, magnetometer_x_rad)
    
    # Convert the yaw angle to degrees
    yaw_degrees = math.degrees(yaw)
    
    # Normalize the compass reading to a range of 0-360 degrees
    compass_reading = (yaw_degrees + 360) % 360
    
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

def nav(packet: comms.Packet, servo: Servo, e: float, 
    last_rotate: float, lsm: sensor.LSM303, gps: sensor.L76x, 
    desiredPos: Tuple[float, float]):
    # global e, last_rotate
    print(packet)
    pitch, roll = calculate_angles(*lsm.getAcceleration())
    # 
    if time.time() < last_rotate + 0.5:
        return

    last_rotate = time.time()

    mag_corected = rotate_vector(pitch, roll, lsm.getMagnetic())
    compass = compass_reading(*mag_corected)
    rotation = get_rotation((gps.getLat(), gps.getLon()), desiredPos)
    rotation_to_do = get_rotation_difference(compass, rotation)
    if rotation_to_do < -e:
        # go Left
        def repeat_function():
            #replace function with function to rotate servo by 45 degrees
            servo.rotate(servo.left)
            start = time.time()
            des_rotation = get_rotation((gps.getLat(), gps.getLon()), desiredPos)
            while compass_reading(*rotate_vector(pitch, roll, lsm.getMagnetic())) < \
                des_rotation - e and time.time() < start+ 0.5:
                pass
                # Add a delay if necessary
                time.sleep(0.020)
            servo.rotate(servo.neutral)
        
    elif rotation_to_do > e:
        # go Right
        def repeat_function():
            #replace function with function to rotate servo by 45 degrees
            function()
            start = time.time()
            des_rotation = get_rotation((gps.getLat(), gps.getLon()), desiredPos)
            while compass_reading(*rotate_vector(pitch, roll, lsm.getMagnetic())) > \
                des_rotation + e and time.time() < start+ 0.5:
                pass
                # Add a delay if necessary
                time.sleep(0.020)
            function()
        
    else:
        def repeat_function():
            pass

    # Create a new thread and start it
    thread = threading.Thread(target=repeat_function)
    thread.start()


def init():
    # global lsm, bme, gps, radio, pitch, roll, desiredPos
    desiredPos = (0,0)
    lsm = sensor.LSM303()
    bme = sensor.BME(i2c=board.I2C())
    comms.SD_o = comms.SD('log.out')
    sensor.SD_o = comms.SD_o
    gps = sensor.L76x()
    radio = comms.Radio(comms.CS, comms.RESET, comms.PWR, comms.FREQ)
    time.sleep(15)
    
    time.sleep(4)
    lsm.mag = calibrate(lsm.mag)
    servo = Servo()
    return lsm, bme, gps, radio, desiredPos, servo


def update(gps, radio, bme, lsm, servo, e, last_rotate, desiredPos):
    gps.refresh()
    Packet = comms.Packet(time.ctime(), temperature=bme.getTemp(), pressure=bme.getPress(), humidity=bme.getHum(), gps_position=(gps.getLat(), gps.getLon()),\
         acceleration= lsm.getAcceleration(), magnetometer_reading= lsm.getMagnetic(), altitude=bme.getAltitude())

    packet = Packet.encode()
    radio.send(packet)
    comms.SD_o.write(packet)
    _in = radio.recv()
    comms.SD_o.write(_in)
    packet = comms.Packet()
    packet.decode(_in)
    print("before check", desiredPos)
    bme.setSeaLevelPressure(packet.pressure if packet.pressure != None else bme.getSeaLevelPressure())
    desiredPos = packet.gps_position if packet.gps_position != None else desiredPos
    print("after check", desiredPos)
    nav(Packet, servo, e, last_rotate, lsm, gps, desiredPos)
    return desiredPos, last_rotate


def main():
    lsm, bme, gps, radio, desiredPos, servo = init()
    last_rotate = 0
    E = 4
    print(f"mainDP {desiredPos}")
    while 1:
        desiredPos, last_rotate = update(gps, radio, bme, lsm, servo, E, last_rotate, desiredPos)


if __name__ =="__main__":
    main()
