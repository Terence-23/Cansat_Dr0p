# file for sensor communication

from multiprocessing import Value, Array, Process, Queue
import adafruit_lsm303_accel
import adafruit_lis2mdl
import time
from lib.L76x import L76X
# import math
import comms
from typing import Tuple
import board
import digitalio
import adafruit_bme680
from adafruit_onewire.bus import OneWireBus
from adafruit_ds18x20 import DS18X20
import os
import globimport math
import numpy as np
from ast import literal_eval as l_eval
import sys, time


def rotate_vector(pitch, roll, vector):
    pitch = math.radians(pitch)
    roll = math.radians(roll)
    x, y, z = vector

    rotated_x = x * math.cos(pitch) + y * math.sin(pitch)
    rotated_y = -x * math.sin(roll) * math.sin(pitch) + \
        y * math.cos(roll) + z * math.sin(roll)
    rotated_z = x * math.cos(roll) * math.sin(pitch) - \
        y * math.sin(roll) + z * math.cos(roll)

    return (rotated_x, rotated_y, rotated_z)


def calculate_angles(acceleration_x, acceleration_y, acceleration_z):
    pitch = math.atan2(acceleration_x, math.sqrt(
        acceleration_y * acceleration_y + acceleration_z * acceleration_z))
    roll = math.atan2(acceleration_y, math.sqrt(
        acceleration_x * acceleration_x + acceleration_z * acceleration_z))
    pitch_degrees = math.degrees(pitch)
    roll_degrees = math.degrees(roll)
    return (pitch_degrees, roll_degrees)


def calibrate():
    hardiron_calibration = np.array(l_eval(open("cal_data").readline()))
    return hardiron_calibration


def compass_reading(magnetometer_x, magnetometer_y, magnetometer_z):
    # Convert the magnetometer readings to radians
    # magnetometer_x_rad = math.radians(magnetometer_x)
    # magnetometer_y_rad = math.radians(magnetometer_y)

    # normvals = normalize(magvals, hardiron_calibration)
    # print("magnetometer: %s -> %s" % (magvals, normvals))

    # # we will only use X and Y for the compass calculations, so hold it level!
    # compass_heading = int(-math.atan2(normvals[2], normvals[1]) * 180.0 / math.pi)
    # raw_compass_heading = int(-math.atan2(magvals[2], magvals[1]) * 180.0 / math.pi)
    # # compass_heading is between -180 and +180 since atan2 returns -pi to +pi
    # # this translates it to be between 0 and 360
    # compass_heading += 450
    # compass_heading %= 360

    # Calculate the yaw angle in radians
    yaw = -math.atan2(magnetometer_z, magnetometer_y)

    # Convert the yaw angle to degrees
    yaw_degrees = math.degrees(yaw)

    # Normalize the compass reading to a range of 0-360 degrees
    compass_reading = (yaw_degrees + 450) % 360

    return compass_reading


def get_rotation(point1, point2):
    x1, y1 = point1
    x2, y2 = point2

    # Calculate the difference between the points
    dx = x2 - x1
    dy = y2 - y1

    # Calculate the angle from the positive x-axis
    angle = math.atan2(dy, dx)

    # Convert the angle from radians to degrees
    angle = math.degrees(angle)

    # Make sure the angle is positive
    if angle < 0:
        angle += 360

    return angle


def normalize(_magvals, hardiron_calibration):
    ret = [0, 0, 0]
    for i, axis in enumerate(_magvals):
        minv, maxv = hardiron_calibration[i]
        axis = min(max(minv, axis), maxv)  # keep within min/max calibration
        ret[i] = (axis - minv) * 200 / (maxv - minv) + -100
    return ret


def get_rotation_difference(current_heading, desired_heading):
    difference = desired_heading - current_heading
    if difference > 180:
        difference -= 360
    elif difference < -180:
        difference += 360
    return difference


def quad_sqrt_function(x):
    x = max(0,min(x, 1))
    numerator = (-1 * math.pow(x - 1, 2) + 1) + math.sqrt(x)
    denominator = 2
    result = numerator / denominator
    return result

def lin_function(x):
    x = max(0,min(x, 1))
    return x


def show_curves():
    git aimport matplotlib.pyplot as plt
    
    x_values = np.linspace(-1, 2, 100)

    # Calculate the corresponding y values
    y_values = [quad_sqrt_function(i) for i in x_values]
    y_values2 = [lin_function(i) for i in x_values]

    # Plot the function
    plt.plot(x_values, y_values)
    plt.plot(x_values, y_values2)

    # Add labels to the plot
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Function plot')

    # Show the plot
    plt.show()
    sys.exit()
    

def steer(max_t, c_t, left, right):
    max_t = abs(max_t)
    if c_t > 0:
        return right * quad_sqrt_function(c_t/max_t)
    else:
        return left * quad_sqrt_function(-c_t/max_t)
    
def steer_target(left, right, neutral, max_t, servo, lsm, gps, desiredPos, sleeping):
    left = left - neutral
    right = right - neutral
    lat = gps[0]
    lon = gps[1]
    hardiron_calibration = np.array(l_eval(open("cal_data").readline()))
    
    while True: 
        if not sleeping.value:
            mag_corected = normalize(
                np.array(lsm.getMagnetic()), hardiron_calibration)
            compass = compass_reading(*mag_corected)
            rotation = get_rotation((lat.value, lon.value), [desiredPos[0].value, desiredPos[1].value])
            rotation_to_do = get_rotation_difference(compass, rotation)
            servo.rotate(neutral + steer(max_t, rotation_to_do, left, right))
        time.sleep(.05)
        
        
    
    

SD_o: comms.SD
PRESSUREHPA = 1013


class BME:
    sensor: adafruit_bme680.Adafruit_BME680
    temp = Value('d',-1000)
    press = Value('d',-1000)
    hum = Value('d',-1000)
    alt = Value('d',-1000)

    log_path = 'Data/BME.out'
    
    def __init__(self, cs=digitalio.DigitalInOut(board.D22), spi=board.SPI(), i2c=None) -> None:
        if i2c != None:
            self.sensor = adafruit_bme680.Adafruit_BME680_I2C(
                i2c, refresh_rate=5)
        else:
            self.sensor = adafruit_bme680.Adafruit_BME680_SPI(spi, cs)

        self.sensor.sea_level_pressure = self.sensor.pressure
        self.sensor.pressure_oversample = 8
        self.rProcess = Process(target=self.refresh)
        self.rProcess.start()

    def refresh(self):
        while True:
            if self.temp.value != self.sensor.temperature or\
                self.press.value != self.sensor.pressure or\
                self.hum.value != self.sensor.humdidty:
                
                self.temp.value = self.sensor.temperature
                self.press.value = self.sensor.pressure
                self.alt.value = self.sensor.altitude
                self.hum.value = self.sensor.humidity
                
                with open(self.temp_path, 'a') as f:
                    f.write(f'{time.time()};{self.temp.value};{self.press.value};{self.hum.value};{self.alt.value}\n')

            time.sleep(0.199)

    def setSeaLevelPressure(self, pressure):
        print(pressure)
        self.sensor.sea_level_pressure = pressure

    def getSeaLevelPressure(self):
        return self.sensor.sea_level_pressure

    def getAltitude(self):
        return self.alt.value

    def getTemp(self):
        return self.temp.value

    def getHum(self):
        return self.hum.value

    def getPress(self):
        return self.press.value


class LSM303:

    acc = Array('d',3)
    magvals = Array('d',3)
    log_path = 'Data/LSM.out'

    def __init__(self, i2c=board.I2C()) -> None:
        self.accel = adafruit_lsm303_accel.LSM303_Accel(i2c)
        self.mag = adafruit_lis2mdl.LIS2MDL(i2c)
        self.mag.data_rate = 3
        self.accel.data_rate = 5
        self.rProcess = Process(target=self.refresh)
        self.rProcess.start()

    def getAcceleration(self) -> Tuple[float, float, float]:
        return self.acc[:]

    def getMagnetic(self) -> Tuple[float, float, float]:
        return self.magvals[:]

    def refresh(self):
        while True:

            if self.accel.acceleration != self.acc[:] or self.mag.magnetic != self.magvals[:]:
                self.acc.get_obj()[:] = self.accel.acceleration
                self.magvals.get_obj()[:] = self.mag.magnetic
                with open(self.log_path, 'a')as f:
                    f.write(f'{time.time()};{";".join(map(str, self.acc[:]))};{";".join(map(str, self.magvals[:]))}\n')

            time.sleep(0.009)


class L76x:

    path = 'Data/gps.out'

    refresh_delay = 1000
    l_rf_time = 0
    gps: L76X.L76X

    def startGPS(self):
        x = L76X.L76X()
        x.L76X_Set_Baudrate(9600)
        x.L76X_Send_Command(x.SET_NMEA_BAUDRATE_115200)
        time.sleep(2)
        x.L76X_Set_Baudrate(115200)
        x.L76X_Send_Command(x.SET_POS_FIX_400MS)
        # Set output message
        x.L76X_Send_Command(x.SET_NMEA_OUTPUT)
        x.L76X_Exit_BackupMode()
        return x

    def __init__(self):
        self.gps = None
        while self.gps == None:
            try:
                self.gps = self.startGPS()
            except Exception as e:
                SD_o.write(comms.FL_ERROR, f'{e}')

        SD_o.write(comms.FL_GPS, 'GPS ready')
        self.refresh()

    def refresh(self, lat=Value('d', 0), lon=Value('d', 0), fix=Value('i', 0)):
        try:
            self.gps.L76X_Gat_GNRMC()
            self.l_rf_time = time.time()*1000
            lat.value = self.gps.Lat
            lon.value = self.gps.Lon
            fix.value = self.gps.Status
            with open(self.path, 'a')as f:
                f.write(
                    f'{time.time()};{self.gps.Lat};{self.gps.Lon};{self.gps.Status}\n')

        except KeyboardInterrupt as e:
            raise e

        except Exception as e:
            print(e)
            SD_o.write(comms.FL_ERROR, f'{e}')

    def getLat(self):
        # if self.l_rf_time + self.refresh_delay <= time.time() * 1000: self.refresh()

        return self.gps.Lat

    def hasFix(self):
        # if self.l_rf_time + self.refresh_delay <= time.time() * 1000: self.refresh()
        return self.gps.Status == 1

    def getLon(self):
        # if self.l_rf_time + self.refresh_delay <= time.time() * 1000: self.refresh()
        return self.gps.Lon


class Dallas:

    temp = Value('d', -10000)
    log_path = 'Data/dallas.out'
    pin = board.D5
    
    
    def read_temp(self):
        with open(self.device_file, 'r') as f:
            lines = f.readlines()
            while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = f.readlines()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c

    def __init__(self) -> None:
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        
        self.base_dir = '/sys/bus/w1/devices/'
        self.device_folder = glob.glob(self.base_dir + '28*')[0]
        self.device_file = self.device_folder + '/w1_slave'
        
        
        self.rProcess = Process(target=self.refresh)
        self.rProcess.start()

    def refresh(self):
        while True:
            temp = self.read_temp()
            if temp != self.temp.value:
                self.temp.value = temp
                with open(self.log_path, 'a') as f:
                    f.write(f'{time.time()};{self.temp.value}\n')


    def GetTemp(self):
        return self.temp.value
