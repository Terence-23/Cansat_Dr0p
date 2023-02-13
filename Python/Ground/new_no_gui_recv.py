#!/bin/python

import sys
sys.path.append('..')

import time
import Can.comms as comms
from Can.new_Packet import Packet, Command
import traceback
import random

radio = comms.Radio()
comms.SD_o = comms.SD("log.txt")

first_timestamp = time.time()


def listen_for_radio():
        while True:
            try:
                print(time.time())
                packet = Packet.decode(radio.recv())
                print(packet.to_json())
                command_packet = Packet.create_command_packet(time.time(), Command.SETPRESS, 20.0)
                radio.send(command_packet.encode())
                
                if not (packet.payload["temp"] is None):
                    comms.SD_o.write(f'{time.time() - first_timestamp} time difference')
                    comms.SD_o.write(str(packet) + 'packet')
                    comms.SD_o.write(str(packet.payload['temp']) + 'tempval')
                    #packet_queue.append(packet)
            except Exception as e:
                traceback.print_exc()
                print(e)

            # Schedule the update function to be called in the main GTK thread
            #GLib.idle_add(self.update)


if __name__ == '__main__':
    listen_for_radio()
