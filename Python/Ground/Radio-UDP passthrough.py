#!/bin/python

import sys

sys.path.append('..')

import Can.comms as comms
from Can.new_Packet import Packet, PacketType, Command

import socket
from random import randint
import time
from ast import literal_eval as l_eval
import threading
import traceback
import math

UDPIPS = ['192.168.100.28', '192.168.100.101']
UDP_LOCAL_IP = '192.168.100.138'
UDP_PORT = 2137
UDP_LOCAL_PORT = 2138

comms.SD_o = comms.SD('UDP server.log')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
with open('cal_data') as f:
    hardiron_calibration = l_eval(f.readline())

radio = comms.Radio(freq=comms.FREQ)

def wait_for_udp():
    sock.bind((UDP_LOCAL_IP, UDP_LOCAL_PORT))
    bufferSize = 1024

    while True:
        bytesAddressPair = sock.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]
        clientMsg = "Message from Client:{}".format(message)
        clientIP  = "Client IP Address:{}".format(address)
        print(clientMsg)
        print(clientIP)
        type, *args = str(message, 'utf-8').strip().split(';')
        
        if type.upper().strip() == "WAKE":
            msg = Packet.create_command_packet(time.time(), Command.WAKE).encode()
            radio.send(msg)
            time.sleep(0.3)
            radio.send(msg)
            print(msg)
        elif type.upper() == "PRESS":
            try:
                msg = Packet.create_command_packet(time.time(), Command.SETPRESS, float(args[0])).encode()
                radio.send(msg)
                time.sleep(0.3)
                radio.send(msg)
                print(msg)
            except Exception as e:
                traceback.print_exc()
        elif type.upper() == "POS":
            try:
                msg = Packet.create_command_packet(time.time(), Command.SETPRESS, float(args[0]), float(args[1])).encode()
                radio.send(msg)
                time.sleep(0.3)
                radio.send(msg)
                print(msg)
            except Exception as e:
                traceback.print_exc()
        else:
            print("Unknown request")
   

def normalize(_magvals, hardiron_calibration):
    ret = [0, 0, 0]
    for i, axis in enumerate(_magvals):
        minv, maxv = hardiron_calibration[i]
        axis = min(max(minv, axis), maxv)  # keep within min/max calibration
        ret[i] = (axis - minv) * 200 / (maxv - minv) + -100
    return ret


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
     

def radio_recv():
    
    last_base = Packet.create_base_packet(0,0,0,0,0)
    last_ext = Packet.create_extended_packet(0,0,0,0,0,0,0,0,0)
    
    while True:
        in_text = radio.recv()
        if in_text is not None:
            try:
                packet = Packet.decode(in_text)
                
                if packet.packet_type == PacketType.BASE:
                    last_base = packet
                elif packet.packet_type == PacketType.EXTENDED:
                    last_ext = packet                    
                
                compass = compass_reading(*normalize(
                    (last_ext.payload['magnetometer_x'], last_ext.payload['magnetometer_y'], last_ext.payload['magnetometer_z']) ,hardiron_calibration))
                
                studio_frame = f"${last_base.encode()[2:]};{';'.join(last_ext.encode().split(';')[2:-3])};{compass}*\n"
                for ip in UDPIPS:
                    sock.sendto(bytes(studio_frame, 'utf-8'),(ip, UDP_PORT))
                
            except Exception as e:
                traceback.print_exc()
    

threading.Thread(target=wait_for_udp).start()
threading.Thread(target=radio_recv).start()

print('start')


try:
    while True:
        time.sleep(1)

except KeyboardInterrupt as e:
    sys.exit()
    


