#!/bin/python

import json
import time
import sys

sys.path.append('..')

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import Can.new_Packet as packet
from matplotlib.animation import FuncAnimation
import numpy as np
import threading
# from scipy.interpolate import interp1d
gdata = []

interval = 0.01

def update(frames):
    global gdata
    xs = [d[0] for d in gdata]
    ys = [d[1] for d in gdata]
    zs = [d[2] for d in gdata]
    # print(gdata)
    ax.clear()
    ax.plot(xs, ys, zs)
    
    

def make_points(data: list[packet.Packet]):
    # divide into basic and extended
    basic = []
    extended = []
    for i in data:
        if i.packet_type == packet.PacketType.BASE:
            basic.append(i)
        elif i.packet_type == packet.PacketType.EXTENDED:
            extended.append(i)

    time_altitude = [float(i.timestamp) for i in basic]
    altitude = [i.payload['altitude'] for i in basic]
    
    time_gps = [float(i.timestamp) for i in extended]
    lats = [i.payload['lat'] for i in extended]
    lons = [i.payload['lon'] for i in extended]
    
    time_nearest = []
    
    for index, v in enumerate(time_gps):
        if index >= len(time_altitude):
            break
        test_index = index
        min_dif = abs(v - time_altitude[index])
        
        min_index = test_index
        if v > time_altitude[index]:
            while test_index >= 0 and v > time_altitude[test_index]:
                if v - time_altitude[test_index] < min_dif:
                    min_dif = v - time_altitude[test_index]
                    min_index = test_index
                test_index +=1
        
        elif v < time_altitude[index]:
            if index > len(time_altitude):
                min_index = len(time_altitude) - 1
            while test_index < len(time_altitude) and v < time_altitude[test_index]:
                if time_altitude[test_index] - v < min_dif:
                    min_dif = time_altitude[test_index] - v
                    min_index = test_index
                test_index +=1
        print (min_index)
        time_nearest.append(min_index)
        
    altitude = [altitude[i] for i in time_nearest]
        
        
    data_out = []
    for a, la, lo in zip(altitude, lats, lons):
        data_out.append((la, lo, a))
    
    return data_out

def release_more_data(data):
        global gdata
        i = 0
        while i < len(data):
            print(i)
            gdata = data[0:i]
            time.sleep(interval)
            i+=1
    

# Example Usage
def main():
    global ax, ani, gdata
    packets = packet.Packet.read_multiple_from_file('/home/p1xel/Documents/CanSat/Cansat/Python/Ground/sampleData.json')
    data = make_points(packets)
    print(data)
    threading.Thread(target=release_more_data, args=(data,)).start()
    # gdata = data
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    ani = FuncAnimation(fig, update, frames=np.linspace(0, 2*np.pi, 2500), repeat=False,  interval=1000 * interval)
    plt.show()
    ani.save('file.mp4')
        
    

if __name__ == "__main__":
    main()
