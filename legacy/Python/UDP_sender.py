import sys

sys.path.append('..')

# import Can.comms
from Can.new_Packet import Packet, PacketType, Command

import socket
from random import randint
import time
from ast import literal_eval as l_eval
import threading

UDP_IP = '127.0.0.1'
UDP_PORT = 2137

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
with open('cal_data') as f:
    hardiron_calibration = l_eval(f.readline())

def wait_for_udp():
    sock.bind(("127.0.0.1", 2138))
    bufferSize = 1024

    while True:
        bytesAddressPair = sock.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]
        clientMsg = "Message from Client:{}".format(message)
        clientIP  = "Client IP Address:{}".format(address)
        print(clientMsg)
        print(clientIP)


threading.Thread(target=wait_for_udp).start()

while True:

    bp = Packet.create_base_packet(time.time(),randint(-10, 40),randint(800, 1100),randint(0,100), randint(1, 2000))
    ep = Packet.create_extended_packet(time.time(),randint(50, 55), randint(20,23), 0.6,0.5,0.2,0.1,0.3,0.4)
    studio_frame = f"${bp.encode()[2:]};{';'.join(ep.encode().split(';')[2:-3])};{0}*\n"
    sock.sendto(bytes(studio_frame, 'utf-8'),(UDP_IP, UDP_PORT))
    time.sleep(0.5)

