#!/bin/python

import random
import sys
import time
sys.path.append("..")

import Can.new_Packet as packet

def generate_sample_data(length, fall_speed, horizontal_speed):
  data = []
  altitude = 2500
  latitude = 50
  longitude = 20
  start_time = time.time()
  
  for i in range(length):
    packet_type = random.choice([0, 1]) # Choose packet Type
    if packet_type == 0: # Packet Type 0 - Altitude
      altitude = altitude - fall_speed # Can't go above sea level
      g_packet = packet.Packet(packet.PacketType.BASE, start_time, payload={'temp': 20, 'press': 1013, 'humidity': 40, 'altitude': altitude})
    else: # Packet Type 1 - GPS Coordinates
      latitude += random.uniform(-horizontal_speed, horizontal_speed)
      longitude += random.uniform(-horizontal_speed, horizontal_speed)
      g_packet = packet.Packet.create_extended_packet(start_time, latitude, longitude, 0, 0, 9.8, 0, 0, 0)
      
            
    data.append(g_packet)
    start_time += 1
  
  return data

# Example Usage
data = generate_sample_data(5000, 5, 0.001/60)

datastr = f'[' +",\n".join(i.to_json() for i in data) + ']' 

with open('sampleData.json', 'w', encoding= 'utf-8') as f:
    f.write(datastr)
    
