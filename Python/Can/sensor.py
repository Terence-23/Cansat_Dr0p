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
        self.accel.data_rate = adafruit_lsm303_accel.Rate(5)
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

    def __init__(self) -> None:
        ow_bus = OneWireBus(self.pin)
        self.ds18 = DS18X20(ow_bus, ow_bus.scan()[0])
        self.ds18.resolution = 12
        self.rProcess = Process(target=self.refresh)
        self.rProcess.start()

    def refresh(self):
        while True:
            if self.ds18.temperature != self.temp.value:
                self.temp.value = self.ds18.temperature
                with open(self.log_path, 'a') as f:
                    f.write(f'{time.time()};{self.temp.value}\n')

            time.sleep(0.125)

    def GetTemp(self):
        return self.temp.value
