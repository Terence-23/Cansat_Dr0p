#!/bin/python3

import math
import board, adafruit_lsm303_accel, adafruit_lis2mdl


class LSM303:
    def __init__(self, i2c=board.I2C()) ->None:
        self.accel = adafruit_lsm303_accel.LSM303_Accel(i2c)
        self.mag = adafruit_lis2mdl.LIS2MDL(i2c)
    def getAcceleration(self):
        return self.accel.acceleration

    def getMagnetic(self):
        return self.mag.magnetic


def calculate_compass_reading(magnetometer_x, magnetometer_y):
  # Convert the magnetometer readings to radians
  magnetometer_x_rad = math.radians(magnetometer_x)
  magnetometer_y_rad = math.radians(magnetometer_y)
  
  # Calculate the yaw angle in radians
  yaw = math.atan2(magnetometer_y_rad, magnetometer_x_rad)
  
  # Convert the yaw angle to degrees
  yaw_degrees = math.degrees(yaw)
  
  # Normalize the compass reading to a range of 0-360 degrees
  compass_reading = (yaw_degrees + 360) % 360
  
  return compass_reading

if __name__ == '__main__':
    mag_x, mag_y, _ = LSM303().getMagnetic()
    print(calculate_compass_reading(mag_x, mag_y))