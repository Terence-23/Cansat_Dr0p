#!/bin/python3
from typing import Tuple
import comms
import sensor
from new_Packet import Packet, PacketType, Command
from ast import literal_eval as l_eval
import numpy as np
import time
import board
import digitalio
import threading
import pwmio
import math
import traceback
from adafruit_motor import servo


class Servo:
    left = 120
    neutral = 65

    right = 20

    def __init__(self, pwm=pwmio.PWMOut(board.D23, frequency=50)) -> None:
        self.s = servo.Servo(pwm, min_pulse=700, max_pulse=2250)

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


def calculate_angles(acceleration_x, acceleration_y, acceleration_z):
    pitch = math.atan2(acceleration_x, math.sqrt(
        acceleration_y * acceleration_y + acceleration_z * acceleration_z))
    roll = math.atan2(acceleration_y, math.sqrt(
        acceleration_x * acceleration_x + acceleration_z * acceleration_z))
    pitch_degrees = math.degrees(pitch)
    roll_degrees = math.degrees(roll)
    return (pitch_degrees, roll_degrees)


def calibrate():
    hardiron_calibration = np.array(l_eval(open("cal_data").readline()))
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


def normalize(_magvals, hardiron_calibration):
    ret = [0, 0, 0]
    for i, axis in enumerate(_magvals):
        minv, maxv = hardiron_calibration[i]
        axis = min(max(minv, axis), maxv)  # keep within min/max calibration
        ret[i] = (axis - minv) * 200 / (maxv - minv) + -100
    return ret

def get_rotation_difference(current_heading, desired_heading):
    difference = desired_heading - current_heading
    if difference > 180:
        difference -= 360
    elif difference < -180:
        difference += 360
    return difference

isturning = False

def main():
    global isturning
    # init
    sleeping = False 
    turn_delay= 1 #seconds
    last_rotate = time.time() -turn_delay
    e = 10
 
    desiredPos = (-90, 0)
    
    comms.SD_o = comms.SD('log.out')
    sensor.SD_o = comms.SD_o
    
    lsm = sensor.LSM303()
    bme = sensor.BME(i2c=board.I2C())
    gps = sensor.L76x()
    radio = comms.Radio(comms.CS, comms.RESET, comms.PWR, comms.FREQ)

    hardiron_calibration = calibrate()
    servo = Servo()
    c_press = bme.getPress()
    sleep_time = time.monotonic()
    sleep_delay = 600
    bme.setSeaLevelPressure(bme.getPress())
    
    print('freq', radio.rfm9x.frequency_mhz)

    while 1:
        packet_b = Packet.create_base_packet(
            time.time(), bme.getTemp(), bme.getPress(), bme.getHum(), bme.getAltitude())

        comms.SD_o.write(comms.FL_PACKET, packet_b.to_json())
        print(packet_b.to_json())
        radio.send(packet_b.encode())
        
        if sleeping:
            in_text = radio.recv(with_ack=True)
            if not in_text is None:
                print(in_text)
                try:
                    in_packet = Packet.decode(in_text)
                            
                    comms.SD_o.write(comms.FL_PACKET, in_packet.to_json())

                    if in_packet.packet_type == PacketType.COMMAND:
                        command = in_packet.payload['command']
                        if command == Command.SLEEP:
                            sleeping = True
                        elif command == Command.WAKE:
                            sleeping = False
                            c_press = bme.getPress()
                            sleep_time = time.monotonic()
                        elif command == Command.SETPOS:
                            desiredPos = in_packet.payload['args']
                            comms.SD_o.write(comms.FL_DEBUG, desiredPos)
                        elif command == Command.SETPRESS:
                            bme.setSeaLevelPressure(in_packet.payload['args'][0])
                            comms.SD_o.write(comms.FL_DEBUG, bme.getSeaLevelPressure())
                        else:
                            comms.SD_o.write(comms.FL_ERROR, 
                                "Invalid command in Packet: {}".format(in_packet.to_json()))
                    else:
                        comms.SD_o.write(comms.FL_ERROR, 
                            "Packet not a command: {}".format(in_packet.to_json()))
                    
                except KeyboardInterrupt as e:
                    raise e
                
                except Exception as e:
                    comms.SD_o.write(comms.FL_ERROR, traceback.format_exc())
                    traceback.print_exc()                
                
            else: 
                comms.SD_o.write(comms.FL_PACKET, 'no Packet recieved')    
        else:

            gps.refresh()

            print(gps.hasFix())

            packet_e = Packet.create_extended_packet(math.floor(time.time()), gps.getLat(), gps.getLon(), *lsm.getAcceleration(), *lsm.getMagnetic())

            radio.send(packet_e.encode())
            print(packet_e.to_json())
            comms.SD_o.write(comms.FL_PACKET, packet_e.to_json())

            pitch, roll = calculate_angles(*lsm.getAcceleration())
            #
            print(f"isturning: {isturning}")
            if isturning:
                continue
            isturning = True
            print("Turning")
            last_rotate = time.time()

            mag_corected = normalize(np.array(lsm.getMagnetic()), hardiron_calibration)
            compass = compass_reading(*mag_corected)
            rotation = get_rotation((gps.getLat(), gps.getLon()), desiredPos)
            rotation_to_do = get_rotation_difference(compass, rotation)
            
            print(f"compass: {compass}, rotation: {rotation}, get_rotation_difference: {rotation_to_do}")

            servo.rotate(servo.right)
            time.sleep(.5)
            servo.rotate(servo.left)

if __name__ == '__main__':
    main()
