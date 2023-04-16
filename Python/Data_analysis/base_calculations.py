import sys

sys.path.append('..')

import math, time
import numpy as np
from ast import literal_eval as l_eval
# from haversine import haversine_distance, Unit


def calc_v_speed(packet, prev_packet):
    return (prev_packet[-1] - packet[-1]) / (packet[0] - prev_packet[0])

def read_packets(path):
    with open(path, 'r') as f:
        return [[i for i in map(float, line.split(','))] for line in f.readlines()]
    

def calc_all_packets(packets):

    post_calc = ['timestamp,temp, press, hum, alt, v_speed, ctime']
    
    packet = packets[0]

    
    v_speed = 0
    
    post_calc.append(','.join(map(str, packet + [v_speed, time.ctime(packet[0])])))
    
    prev_packet = packet
    for packet in packets[1:]:   
        #packet independent

        
        #packet dependent
        v_speed = calc_v_speed(packet, prev_packet)
        
        if math.floor(prev_packet[0]) != math.floor(packet[0]):
            post_calc.append(','.join(map(str, packet + [v_speed, time.ctime(packet[0])])))
            
            prev_packet = packet
    
    post_calc_csv = '\n'.join(post_calc)
    print(post_calc_csv)
    with open('base_c.csv', 'w') as f:
        f.write(post_calc_csv)
        
calc_all_packets(read_packets('base.csv'))