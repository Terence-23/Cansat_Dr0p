
import numpy as np
import math
from bisect import bisect_left
from haversine import Unit, haversine_distance
import os
import bpy
from scipy.interpolate import interp1d
from ast import literal_eval as l_eval
import sys

path = '/home/ardoni/Cansat/Python/Data_analysis'
# path = 'C:\Users\user\Desktop\CanSat\Python\Data_analysis'

sys.path.append(path)

os.chdir(path)


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


def prepare_data(path='Data/'):
    with open(path + 'raw_data/gps.out') as f:
        gps = [[float(j) for j in i.strip().split(',')]
               for i in f.readlines()[1:]]

    with open(path + 'raw_data/BME.out') as f:
        bme = [[float(j) for j in i.strip().split(',')]
               for i in f.readlines()[1:]]

#    read lats and lons
    lats = [i[1] for i in gps]
    lons = [i[2] for i in gps]

    # headings = [i[9] for i in ext_csv]
    # des_headings = [i[10] for i in ext_csv]
    des_pos = bpy.data.objects['target point marker'].location

    max_lat = max(lats)
    min_lat = min(lats)
    avg_lat = (max_lat + min_lat)/2

    max_lon = max(lons)
    min_lon = min(lons)
    avg_lon = (max_lon + min_lon)/2

    lat_span = haversine_distance(
        (min_lat, avg_lon), (max_lat, avg_lon), Unit.METERS)

    lon_span = haversine_distance(
        (avg_lat, min_lon), (avg_lat, max_lon), Unit.METERS)
#    map lats and lons
    lat_int = interp1d([min_lat, max_lat], [-lat_span/2, lat_span/2])
    lon_int = interp1d([min_lon, max_lon], [-lon_span/2, lon_span/2])

    lats = lat_int(lats)
    lons = lon_int(lons)

    alts = []
    for i in [i[0] for i in gps]:
        ind = bisect_left([j[0] for j in bme], i)
        alts.append(bme[ind][4])

    #    raise Exception(f'{len(lons)}, {len(lats)}, {len(alts)}') print workaround

    #    zip lons,lats, and altitude and headings

    headings = []
    hardiron = np.array(l_eval(open("cal_data").readline()))
    with open(path + 'raw_data/LSM.out', 'r') as f:
        lsm = [[j for j in i.strip().split(';')] for i in f.readlines()]
        timestamps = [j[0] for j in lsm]
        for i in (i[0] for i in gps):
            ind = bisect_left(timestamps, i)
            headings.append(compass_reading(
                *normalize(lsm[ind][4:7], hardiron)))

    des_headings = [np.degrees(-np.arctan2(des_pos[0] - x, des_pos[1] - y))
                    for y, x in zip(lats, lons)]
    return zip(lons, lats, alts), zip(headings, des_headings)


positions, headings = prepare_data()

can = bpy.data.objects['CanSat']

start_loc = can.location

opt_pointer = bpy.data.objects['desired_vector']
start_rot = can.rotation_euler
rad90 = math.radians(90)
can.rotation_euler = start_rot

for i, (loc, (heading, opt_heading)) in enumerate(zip(positions, headings)):
    frame = i * 10

    can.location = loc
    can.rotation_euler = (rad90, 0, math.radians(heading))
    can.keyframe_insert('location', frame=frame)
    can.keyframe_insert('rotation_euler', frame=frame)

    opt_pointer.rotation_euler = (
        0, -rad90, math.radians(opt_heading - heading+90))
    opt_pointer.keyframe_insert('rotation_euler', frame=frame)
#    bpy.data.worlds["World"].node_tree.nodes["Sky Texture"].altitude = loc[2]
#    bpy.data.worlds['World'].node_tree.nodes['Sky Texture'].keyframe_insert('altitude', frame=frame)


can.location = start_loc
