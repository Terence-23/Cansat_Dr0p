
import os
import bpy
from scipy.interpolate import interp1d
import sys

path = '/mnt/Data/Programowanie/Cansat/Python/Data_analysis'

sys.path.append(path)

os.chdir(path)

from haversine import Unit, haversine_distance
from bisect import bisect_left
import math

def prepare_data():
    with open('extended_c.csv') as f:
        ext_csv = [[float(j) for j in i.strip().split(',')[:-1]] for i in f.readlines()[1:]]
    
    with open('base_c.csv') as f:
        b_csv = [[float(j) for j in i.strip().split(',')[:-1]] for i in f.readlines()[1:]]

#    read lats and lons
    lats = [i[1] for i in ext_csv]
    lons = [i[2] for i in ext_csv]
    
    headings = [i[9] for i in ext_csv]
    des_headings = [i[10] for i in ext_csv]

    max_lat = max(lats)
    min_lat = min(lats)
    avg_lat = (max_lat + min_lat)/2

    max_lon = max(lons)
    min_lon = min(lons)
    avg_lon = (max_lon + min_lon)/2

    lat_span = haversine_distance((min_lat, avg_lon), (max_lat, avg_lon), Unit.METERS)

    lon_span = haversine_distance((avg_lat, min_lon), (avg_lat, max_lon), Unit.METERS)
#    map lats and lons
    lat_int = interp1d([min_lat, max_lat], [-lat_span/2, lat_span/2])
    lon_int = interp1d([min_lon, max_lon], [-lon_span/2, lon_span/2])

    lats = lat_int(lats)
    lons = lon_int(lons)
    
    alts = []
    for i in [i[0] for i in ext_csv]:
        ind = bisect_left([j[0] for j in b_csv], i)
        alts.append(b_csv[ind][4])
    
        
#    raise Exception(f'{len(lons)}, {len(lats)}, {len(alts)}') print workaround
    
#    zip lons,lats, and altitude and headings
    return zip(lons, lats, alts), zip(headings, des_headings)

   
positions, headings = prepare_data()

can = bpy.data.objects['Cansat']

start_loc = can.location

opt_pointer = bpy.data.objects['opt_looking_direction']
start_rot = can.rotation_euler
rad90 = math.radians(90)
can.rotation_euler = start_rot

for i, (loc, (heading, opt_heading)) in enumerate(zip(positions, headings)):
    frame = i * 10
    
    can.location = loc
    can.rotation_euler = (rad90,0, math.radians(heading))
    can.keyframe_insert('location', frame=frame)
    can.keyframe_insert('rotation_euler', frame=frame)
    
    opt_pointer.rotation_euler = (0,-rad90, math.radians(opt_heading - heading))
    opt_pointer.keyframe_insert('rotation_euler', frame=frame)

    
can.location=start_loc
    

