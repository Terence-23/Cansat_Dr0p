import math
import numpy as np
import matplotlib.pyplot as plt
from ast import literal_eval as l_eval
import sys, time


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


def quad_sqrt_function(x):
    x = max(0,min(x, 1))
    numerator = (-1 * math.pow(x - 1, 2) + 1) + math.sqrt(x)
    denominator = 2
    result = numerator / denominator
    return result

def lin_function(x):
    x = max(0,min(x, 1))
    return x


def show_curves():
    x_values = np.linspace(-1, 2, 100)

    # Calculate the corresponding y values
    y_values = [quad_sqrt_function(i) for i in x_values]
    y_values2 = [lin_function(i) for i in x_values]

    # Plot the function
    plt.plot(x_values, y_values)
    plt.plot(x_values, y_values2)

    # Add labels to the plot
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Function plot')

    # Show the plot
    plt.show()
    sys.exit()
    

def steer(max_t, c_t, left, right):
    max_t = abs(max_t)
    if c_t > 0:
        return right * quad_sqrt_function(c_t/max_t)
    else:
        return left * quad_sqrt_function(-c_t/max_t)
    
def steer_target(left, right, neutral, max_t, servo, lsm, gps, desiredPos, sleeping):
    left = left - neutral
    right = right - neutral
    lat = gps[0]
    lon = gps[1]
    hardiron_calibration = np.array(l_eval(open("cal_data").readline()))
    
    while True: 
        if not sleeping.value:
            mag_corected = normalize(
                np.array(lsm.getMagnetic()), hardiron_calibration)
            compass = compass_reading(*mag_corected)
            rotation = get_rotation((lat.value, lon.value), [desiredPos[0].value, desiredPos[1].value])
            rotation_to_do = get_rotation_difference(compass, rotation)
            servo.rotate(neutral + steer(max_t, rotation_to_do, left, right))
        time.sleep(.05)
        
        
    
    