#!/bin/python3

import time
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


def calculate_angles(acceleration_x, acceleration_y, acceleration_z):
  pitch = math.atan2(acceleration_x, math.sqrt(acceleration_y * acceleration_y + acceleration_z * acceleration_z))
  roll = math.atan2(acceleration_y, math.sqrt(acceleration_x * acceleration_x + acceleration_z * acceleration_z))
  pitch_degrees = math.degrees(pitch)
  roll_degrees = math.degrees(roll)
  return (pitch_degrees, roll_degrees)

yaw_min, yaw_max = 0, 0


def calculate_compass_reading(magnetometer_x, magnetometer_y): 
    global yaw_min, yaw_max
    # Convert the magnetometer readings to radians
    magnetometer_x_rad = math.radians(magnetometer_x)
    magnetometer_y_rad = math.radians(magnetometer_y)
    
    # Calculate the yaw angle in radians
    yaw = math.atan2(magnetometer_y, magnetometer_x)
    
    # Convert the yaw angle to degrees
    yaw_degrees = math.degrees(yaw)
    
    # Normalize the compass reading to a range of 0-360 degrees
    compass_reading = (yaw_degrees + 360) % 360
    yaw_min = min(yaw_degrees, yaw_min)
    yaw_max = max(yaw_max, yaw_degrees)
    
    #   return compass_reading
    return compass_reading


def calibrate(magnetometer:adafruit_lis2mdl.LIS2MDL):
    start_time = time.monotonic()
    hardiron_calibration = [[1000, -1000], [1000, -1000], [1000, -1000]]

    # Update the high and low extremes
    while time.monotonic() - start_time < 10.0:
        magval = magnetometer.magnetic
        print("Calibrating - X:{0:10.2f}, Y:{1:10.2f}, Z:{2:10.2f} uT".format(*magval))
        for i, axis in enumerate(magval):
            hardiron_calibration[i][0] = min(hardiron_calibration[i][0], axis)
            hardiron_calibration[i][1] = max(hardiron_calibration[i][1], axis)
    print("Calibration complete:")
    print("hardiron_calibration =", hardiron_calibration)

    # Calculate biases and scaling factors for the x-axis
    bias_x = (hardiron_calibration[0][0] + hardiron_calibration[0][1]) / 2
    scaling_factor_x = (hardiron_calibration[0][1] - hardiron_calibration[0][0]) / 2

    # Calculate biases and scaling factors for the y-axis
    bias_y = (hardiron_calibration[1][0] + hardiron_calibration[1][1]) / 2
    scaling_factor_y = (hardiron_calibration[1][1] - hardiron_calibration[1][0]) / 2

    # Calculate biases and scaling factors for the z-axis
    bias_z = (hardiron_calibration[2][0] + hardiron_calibration[2][1]) / 2
    scaling_factor_z = (hardiron_calibration[2][1] - hardiron_calibration[2][0]) / 2

    # Assign biases to the offset property
    magnetometer.offset = (bias_x, bias_y, bias_z)
    magnetometer.x_offset, magnetometer.y_offset, magnetometer.z_offset = bias_x, bias_y, bias_z

    # Assign scaling factors to the scale property
    magnetometer.scale = (scaling_factor_x, scaling_factor_y, scaling_factor_z)

    return magnetometer



if __name__ == "__main__":
    
    mag = LSM303().mag
    print("prepare to rotate magnetometer in 3d")
    time.sleep(3)
    mag = calibrate(mag)
    try: 
        while True:
            print(calculate_compass_reading(mag.magnetic[0], mag.magnetic[1]))
            time.sleep(0.2)
    except KeyboardInterrupt as e:
        print(f"min: {yaw_min}, max: {yaw_max}")

    
    


