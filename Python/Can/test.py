#!/bin/python3

import board
import comms, sensor
from time import sleep


def main():
    bme = sensor.BME(i2c = board.I2C())
    lsm = sensor.LSM303(board.I2C())

    while 1:
        print(bme.getAltitude())
        print(lsm.getAcceleration())
        sleep(0.5)


if __name__ == "__main__":
    main()

