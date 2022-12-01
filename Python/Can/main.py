#!/bin/python3
import comms, sensor
import time

def main():
    comms.SD_o = comms.SD('log.out')
    lsm = sensor.LSM303()

    while 1:
        time.sleep(1)
        print(f"Acceleration(m/s^2) {lsm.getAcceleration()}\n Magnetic(uTeslas){lsm.getMagnetic()}")


if __name__ =="__main__":
    main()
