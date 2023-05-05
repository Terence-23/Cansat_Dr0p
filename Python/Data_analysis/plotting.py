import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from bisect import bisect_left
import sys
import math
from ast import literal_eval as l_eval
from haversine import Unit, haversine_distance
from numpy import arctan2 as atan2


def v_length(x, y, z=None) -> float:
    if z is None:
        return np.sqrt(x*x + y*y)
    return np.sqrt(x*x + y*y + z*z)


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


# Headings
def heading(path='Data/raw_data', start_time=0, end_time=None):

    fig, ax = plt.subplots(figsize=(16, 9), layout='constrained')
    hardiron = np.array(l_eval(open("cal_data").readline()))
    desired_pos = 50.3369282, 19.5322675

    if end_time is not None:
        def f(a): return a[0] > start_time
    else:
        def f(a): return a[0] > start_time and a[0] < end_time

    with open(path + 'gps.out', 'r') as f:
        gps = filter(f, [[float(j) for j in i.strip().split(';')]
                         for i in f.readlines()])

    with open(path + 'LSM.out', 'r') as f:
        lsm = filter(f, [[float(j) for j in i.strip().split(';')]
                         for i in f.readlines()])

    timestamps = [i[0] for i in lsm]

    deltatime = timestamps[-1] - timestamps[0]
    polling_rate = len(timestamps) / deltatime

    headings = [compass_reading(*normalize(i[4:7], hardiron)) for i in lsm]
    des_headings = [get_rotation(i[1:3], desired_pos) for i in gps]

    # Plot some data on the axes.
    ax.plot(np.linspace(0, len(headings), len(headings)),
            headings, label='heading')
    # Plot more data on the axes...

    ax2 = ax.twiny()
    ax2.plot(np.linspace(0, len(des_headings), len(des_headings)),
             des_headings, label='optimal heading')
    # Add an x-label to the axes.
    ax.set_xlabel(f'No. of data point. Polling rate: {polling_rate:.3f}Hz')

    timestamps = [i[0] for i in gps]
    deltatime = timestamps[-1] - timestamps[0]
    polling_rate = len(timestamps) / deltatime

    ax2.set_xlabel(f'No. of data point. Polling rate: {polling_rate:.3f}Hz')

    ax.set_ylabel('deg')
    ax.set_title("Heading vs. desired heading")  # Add a title to the axes.

    fig.legend(loc='upper right')
    fig.savefig('Renders/You spin me round.png', dpi=400)

# Press and Alt


def pressure(path='Data/raw_data', start_time=0, end_time=None):

    if end_time is not None:
        def f(a): return a[0] > start_time
    else:
        def f(a): return a[0] > start_time and a[0] < end_time

    with open(path + 'BME.out', 'r') as f:
        packets = filter(f, [[float(j) for j in i.strip().split(';')]
                         for i in f.readlines()])

    press = [i[2] for i in packets]
    alts = [i[4] for i in packets]
    timestamps = [i[0] for i in packets]
    packet_num = np.linspace(0, len(alts), len(alts))

    deltatime = timestamps[-1] - timestamps[0]
    polling_rate = len(timestamps) / deltatime

    fig, ax = plt.subplots(figsize=(16, 9), layout='constrained')

    ax.plot(packet_num, press, label='Pressure')  # Plot some data on the axes.
    # Add an x-label to the axes.
    ax.set_xlabel(f'No. of data point. Polling rate: {polling_rate:.3f}Hz')
    ax.set_ylabel('hPa')

    ax2 = ax.twinx()
    ax2.plot(packet_num, alts, label='Altitude', color='red')
    ax2.set_ylabel('m')  # Plot more data on the axes...

    ax.set_title("Pressure & altitude")  # Add a title to the axes.

    fig.legend(loc='upper right')
    fig.savefig('Renders/Presssure & altitude.png', dpi=400)

# Temp and Hum


def temp_hum(path='Data/raw_data', start_time=0, end_time=None):

    if end_time is not None:
        def f(a): return a[0] > start_time
    else:
        def f(a): return a[0] > start_time and a[0] < end_time

    with open(path + 'BME.out', 'r') as file:
        packets = list(
            filter(f, [[float(j) for j in i.strip().split(';')] for i in file.readlines()]))
    with open(path + 'dallas.out', 'r') as file:
        dallas = filter(f, [[float(j) for j in i.strip().split(';')]
                        for i in file.readlines()])

    temps = [i[1] for i in dallas]
    timestamps = [i[0] for i in dallas]

    hums = [packets[bisect_left(packets, [i], key=lambda a: a[0])][3]
            for i in timestamps]
    packet_num = np.linspace(0, len(timestamps), len(timestamps))
    deltatime = timestamps[-1] - timestamps[0]
    polling_rate = len(timestamps) / deltatime

    fig, ax = plt.subplots(figsize=(16, 9), layout='constrained')

    # Plot some data on the axes.
    ax.plot(packet_num, temps, label='Temperature')
    # Add an x-label to the axes.
    ax.set_xlabel(f'No. of data point. Polling rate: {polling_rate:.3f}Hz')
    ax.set_ylabel('°C')

    ax2 = ax.twinx()
    ax2.plot(packet_num, hums, label='Relative humidity', color='red')
    ax2.set_ylabel('%')  # Plot more data on the axes...

    ax.set_title("Temperature & humidity")  # Add a title to the axes.

    fig.legend(loc='upper right')
    fig.savefig('Renders/Temperature & humidity.png', dpi=400)

# speeds


def speeds(path='Data/raw_data', start_time=0, end_time=None):
    # read data between timestamps
    if end_time is not None:
        def f(a): return a[0] > start_time
    else:
        def f(a): return a[0] > start_time and a[0] < end_time

    with open(path + 'GPS.out', 'r') as f:
        gps = filter(f, ([float(j) for j in i.strip().split(';')]
                     for i in f.readlines()))

    with open(path + 'BME.out', 'r') as f:
        bme = filter(f, ([float(j) for j in i.strip().split(';')]
                     for i in f.readlines()))

    # prepare intermediate data
    lats = [i[1] for i in gps]
    lons = [i[2] for i in gps]

    timestamps = [i[0] for i in gps]

    alts = [bme[bisect_left(bme, [i], key=lambda a: a[0])][4]
            for i in timestamps]

    # prepare data
    h_speeds = [0]

    for i in range(1, len(lats)):
        h_speeds.append(haversine_distance([lats[i], lons[i]], [
                        lats[i-1], lons[i-1]], Unit.METERS))

    v_speeds = [0]
    for i in range(1, len(alts)):
        v_speeds.append(alts[i-1] - alts[i])

    packet_num = np.linspace(0, len(lats), len(lats))

    deltatime = timestamps[-1] - timestamps[0]
    polling_rate = len(timestamps) / deltatime

    fig, ax = plt.subplots(figsize=(16, 9), layout='constrained')

    # Plot some data on the axes.
    ax.plot(packet_num, h_speeds, label='Horizontal speed')
    # Add an x-label to the axes.
    ax.set_xlabel(f'No. of data point. Polling rate: {polling_rate:.3f}Hz')
    ax.set_ylabel('m/s')
    ax.plot(packet_num, v_speeds, label='Vertical speed')

    ax.set_title("Speed")  # Add a title to the axes.

    fig.legend(loc='upper right')
    fig.savefig('Renders/I am speed.png', dpi=400)

# acceleration


def acceleration(path='Data/raw_data', start_time=0, end_time=None, start_val=-100):

    if end_time is not None:
        def f(a): return a[0] > start_time
    else:
        def f(a): return a[0] > start_time and a[0] < end_time

    with open(path + 'LSM.out', 'r') as f:
        packets = filter(
            f, ([float(j) for j in i.strip().split(';')] for i in f.readlines()))

    accs = [v_length(*i[1:4]) for i in packets]
    timestamps = [i[0] for i in packets]

    packet_num = np.linspace(start_val, len(accs) + start_val, len(accs))

    deltatime = timestamps[-1] - timestamps[0]
    polling_rate = len(timestamps) / deltatime

    fig, ax = plt.subplots(figsize=(16, 9), layout='constrained')

    # Plot some data on the axes.
    ax.plot(packet_num, accs, label='Acceleration')
    # Add an x-label to the axes.
    ax.set_xlabel(f'No. of data point. Polling rate: {polling_rate:.3f}Hz')
    ax.set_ylabel('m/s²')

    ax.set_title("Acceleration")  # Add a title to the axes.

    fig.legend(loc='upper right')
    fig.savefig('Renders/Gravity.png', dpi=400)


def main():
    start_time = 0
    end_time = 0
    start_val = -100
    
    heading(start_time=start_time, end_time=end_time)
    pressure(start_time=start_time, end_time=end_time)
    temp_hum(start_time=start_time, end_time=end_time)
    speeds(start_time=start_time, end_time=end_time)
    acceleration(start_time=(start_time + start_val), end_time=end_time, start_val=start_val)
    

    plt.show()


if __name__ == '__main__':
    main()