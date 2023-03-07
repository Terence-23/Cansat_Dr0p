#!/bin/python3

import time
import math
import board, adafruit_lsm303_accel, adafruit_lis2mdl

hardiron_calibration = [[1000, -1000], [1000, -1000], [1000, -1000]]


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



def calculate_compass_reading(magnetometer_x, magnetometer_y, magnetometer_z): 
    global yaw_min, yaw_max
    # Convert the magnetometer readings to radians
    magnetometer_x_rad = math.radians(magnetometer_x)
    magnetometer_y_rad = math.radians(magnetometer_y)
    
    # Calculate the yaw angle in radians
    yaw = -math.atan2(magnetometer_z, magnetometer_y)
    
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

    # Update the high and low extremes
    while time.monotonic() - start_time < 15.0:
        magval = magnetometer.magnetic
        print("Calibrating - X:{0:10.2f}, Y:{1:10.2f}, Z:{2:10.2f} uT".format(*magval))
        for i, axis in enumerate(magval):
            hardiron_calibration[i][0] = min(hardiron_calibration[i][0], axis)
            hardiron_calibration[i][1] = max(hardiron_calibration[i][1], axis)
    print("Calibration complete:")
    print("hardiron_calibration =", hardiron_calibration)

    with open('cal_data', 'w') as f:
        f.write(str(hardiron_calibration))

    # # Calculate biases and scaling factors for the x-axis
    # bias_x = (hardiron_calibration[0][0] + hardiron_calibration[0][1]) / 2
    # scaling_factor_x = (hardiron_calibration[0][1] - hardiron_calibration[0][0]) / 2

    # # Calculate biases and scaling factors for the y-axis
    # bias_y = (hardiron_calibration[1][0] + hardiron_calibration[1][1]) / 2
    # scaling_factor_y = (hardiron_calibration[1][1] - hardiron_calibration[1][0]) / 2

    # # Calculate biases and scaling factors for the z-axis
    # bias_z = (hardiron_calibration[2][0] + hardiron_calibration[2][1]) / 2
    # scaling_factor_z = (hardiron_calibration[2][1] - hardiron_calibration[2][0]) / 2

    # # Assign biases to the offset property
    # magnetometer.offset = (bias_x, bias_y, bias_z)
    # magnetometer.x_offset, magnetometer.y_offset, magnetometer.z_offset = bias_x, bias_y, bias_z

    # # Assign scaling factors to the scale property
    # magnetometer.scale = (scaling_factor_x, scaling_factor_y, scaling_factor_z)

    return magnetometer

def normalize(_magvals, hardiron_calibration):
    ret = [0, 0, 0]
    for i, axis in enumerate(_magvals):
        minv, maxv = hardiron_calibration[i]
        axis = min(max(minv, axis), maxv)  # keep within min/max calibration
        ret[i] = (axis - minv) * 2 / (maxv - minv) + -1
    return ret

if __name__ == "__main__":
    
    mag = LSM303().mag
    print("prepare to rotate magnetometer in 3d")
    time.sleep(3)
    mag = calibrate(mag)
    try: 
        while True:
            magvals = mag.magnetic
            normvals = normalize(magvals, hardiron_calibration)
            print("magnetometer: %s -> %s" % (magvals, normvals))

            # we will only use X and Y for the compass calculations, so hold it level!
            compass_heading = int(-math.atan2(normvals[2], normvals[1]) * 180.0 / math.pi)
            raw_compass_heading = int(-math.atan2(magvals[2], magvals[1]) * 180.0 / math.pi)
            # compass_heading is between -180 and +180 since atan2 returns -pi to +pi
            # this translates it to be between 0 and 360
            compass_heading += 450
            compass_heading %= 360
            
            yaw_min = min(compass_heading, yaw_min)
            yaw_max = max(yaw_max, compass_heading)

            print(f"Heading z, y: {compass_heading}, raw {raw_compass_heading}")
            time.sleep(0.1)
    except KeyboardInterrupt as e:
        print(f"min: {yaw_min}, max: {yaw_max}")

    
    


