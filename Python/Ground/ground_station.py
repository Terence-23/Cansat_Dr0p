import comms

import board
from time import ctime

def main():
    radio = comms.Radio(comms.CS, comms.RESET, comms.PWR, comms.FREQ)
    comms.SD_o = comms.SD('log.txt')

    while 1:
        packet = comms.Packet(radio.recv())
        comms.SD_o.write(packet)
        packet = comms.Packet(timestamp=ctime(), gps_position=(0, 0))
        comms.SD_o.write(f"OUT: {packet}")
        radio.send(str(packet))



if __name__ == "__main__":
    main()