#!/bin/python3
import comms, sensor
import time

def main():
    comms.SD_o = comms.SD('log.out')
    comms.Packet.decode("w11;a10;o11;p;h")

    sensor.SD_o = comms.SD_o

    gps = sensor.L76x()
    while 1:
        gps.refresh()
        print(f"Has Fix: {gps.hasFix()}")
        print(f"Lat: {gps.getLat()} Lon: {gps.getLon()}")
        time.sleep(0.99)

if __name__ =="__main__":
    main()