#!/bin/python

import sys
sys.path.append('..')

import time
import Can.comms as comms
from Can.comms import Packet as Packet

radio = comms.Radio()
comms.SD_o = comms.SD("log.txt")

first_timestamp = time.time()


def listen_for_radio():
        while True:
            packet = Packet(timestamp=time.ctime(), temperature=None)
            packet.decode(radio.recv())
            if not (packet.temperature is None):
                comms.SD_o.write(f'{time.time() - first_timestamp} time difference')
                comms.SD_o.write(str(packet) + 'packet')
                comms.SD_o.write(str(packet.temperature) + 'tempval')
                #packet_queue.append(packet)

            # Schedule the update function to be called in the main GTK thread
            #GLib.idle_add(self.update)


if __name__ == '__main__':
    listen_for_radio()
