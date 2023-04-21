#!/bin/python3

import board
import comms, sensor
import time


def main():
    comms.SD_o = comms.SD("log.txt")
    sensor.SD_o = comms.SD_o
    gps = sensor.L76x()
    radio = comms.Radio()
    bme = sensor.BME(i2c=board.I2C())
    lsm=sensor.LSM303()

    while 1:
        gps.refresh()
        packet = comms.Packet(time.ctime(),bme.getTemp(), bme.getPress(), bme.getHum(),  (gps.getLon() if gps.hasFix() else 1/3, gps.getLat() if gps.hasFix() else 1/3), (0,0,0), (0,0,0),  bme.getAltitude())
        print(packet)
        radio.send(packet.encode())
        


if __name__ == "__main__":
    comms.SD_o = comms.SD("log.txt")
    main()

