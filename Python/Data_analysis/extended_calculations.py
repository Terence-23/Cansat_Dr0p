import sys

sys.path.append('..')

import math, time
from numpy import arctan2 as atan2
import numpy as np
from ast import literal_eval as l_eval
from haversine import haversine_distance, Unit

def normalize(_magvals, hardiron_calibration):
    ret = [0, 0, 0]
    for i, axis in enumerate(_magvals):
        minv, maxv = hardiron_calibration[i]
        axis = min(max(minv, axis), maxv)  # keep within min/max calibration
        ret[i] = (axis - minv) * 200 / (maxv - minv) + -100
    return ret

def compass_reading(magnetometer_x, magnetometer_y, magnetometer_z):
    
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

    print(dx, dy)
    # Calculate the angle from the positive x-axis
    angle = atan2(dy, dx)
    
    assert atan2(dy, dx) == math.atan2(dy, dx)

    # Convert the angle from radians to degrees
    angle = math.degrees(angle)

    # Make sure the angle is positive
    angle = (angle + 360) % 360

    return angle

def get_rotation_difference(current_heading, desired_heading):
    difference = desired_heading - current_heading
    if difference > 180:
        difference -= 360
    elif difference < -180:
        difference += 360
    return difference

def calc_heading(packet, hardiron_calibration):
    magvals = packet[6:9]
    return compass_reading(*normalize(magvals, hardiron_calibration))

def calc_optimal_heading(packet, desired_pos):
    print(packet, desired_pos)
    return get_rotation(packet[1:3], desired_pos)

def calc_horizontal_speed(packet, prev_packet):
    point1 = prev_packet[1:3]
    point2 = packet[1:3]
    print(packet, prev_packet)
    deltatime = packet[0] - prev_packet[0]
    distance = haversine_distance(point1, point2, Unit.METERS)
    if deltatime == 0:
        return -1000000
    #meters per second:
    return distance/deltatime

def calc_turn(packet, hardiron_calibration, desired_pos):
    mag_corected = normalize(packet[6:9], hardiron_calibration)
    compass = compass_reading(*mag_corected)
    rotation = get_rotation(packet[1:3], desired_pos)
    rotation_to_do = get_rotation_difference(compass, rotation)
    e = 10
        
    if rotation_to_do < -e:
        # go Left
        return 1
    
    elif rotation_to_do > e:
        # go Right
        return -1
    
    else:
        return 0
    
# hardiron = np.array(l_eval(open("cal_data").readline()))
# desired_pos = 50.3369282, 19.5322675 

def read_packets(path):
    with open(path, 'r') as f:
        return [[i for i in map(float, line.split(','))] for line in f.readlines()]
    
def calc_all_packets(packets):
    hardiron = np.array(l_eval(open("cal_data").readline()))
    desired_pos = 50.3369282, 19.5322675 
    
    post_calc = ['timestamp,lat,lon,acc_ximport ,acc_y,acc_z,mag_x,mag_y,mag_z,heading,opt_heading,hor_speed, ctime, turn_status']
    
    packet = packets[0]
    
    heading = calc_heading(packet,hardiron)
    des_heading = calc_optimal_heading(packet, desired_pos)
    
    h_speed = 0
    
    post_calc.append(','.join(map(str, packet + [heading, des_heading, h_speed, time.ctime(packet[0])])))
    
    prev_packet = packet
    for packet in packets[1:]:   
        #packet independent
        heading = calc_heading(packet, hardiron)
        des_heading = calc_optimal_heading(packet, desired_pos)
        turn_status = calc_turn(packet, hardiron, desired_pos)
        
        #packet dependent
        h_speed = calc_horizontal_speed(packet, prev_packet)
        if h_speed == -1000000:
            h_speed = float(post_calc[-1].split(',')[11])
        
        if prev_packet[0] != packet[0]:
            post_calc.append(','.join(map(str, packet + [heading, des_heading, h_speed, time.ctime(packet[0]), turn_status])))
            
            prev_packet = packet
    
    post_calc_csv = '\n'.join(post_calc)
    # print(post_calc_csv)
    with open('Data/extended_c.csv', 'w') as f:
        f.write(post_calc_csv)
    
calc_all_packets(read_packets('Data/extended.csv'))