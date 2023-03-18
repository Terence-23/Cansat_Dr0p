#!/bin/python

import sensor
from comms import SD
from traceback import print_exc

def main():
    sensor.SD_o = SD('gps_test.log')
    gps = sensor.L76x()

    while True:
        try:
            gps.refresh()

            print(f'Fix: {gps.hasFix()}, lat: {gps.getLat()}, lon: {gps.getLon()}')
            sensor.SD_o.write("GPS", f'Fix: {gps.hasFix()}, lat: {gps.getLat}, lon: {gps.getLon()}')

        except KeyboardInterrupt as e:
            break
        except Exception as e:
            print_exc()


if __name__ == "__main__":
    main()
