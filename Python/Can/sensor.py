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
    sensor:adafruit_bme680.Adafruit_BME680
    temp = -1000
    press = -1000
    hum = -1000
    alt = -1000
    
    temp_path = 'Data/temp.out'
    # pressure and altitude in the same file
    press_path = 'Data/press.out'
    hum_path = 'Data/hum.out'
    
    def __init__(self, cs = digitalio.DigitalInOut(board.D22), spi = board.SPI(), i2c = None) -> None:
        if i2c != None:
            self.sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c, refresh_rate=5)
        else:
            self.sensor = adafruit_bme680.Adafruit_BME680_SPI(spi, cs)

        self.sensor.sea_level_pressure = self.sensor.pressure
        self.sensor.pressure_oversample = 8
        self.rProcess = Process(target=self.refresh)
        self.rProcess.start()        
    
    def refresh(self):
        while True:
            if self.temp != self.sensor.temperature:
                self.temp = self.sensor.temperature  
                with open(self.temp_path, 'a') as f:
                    f.write(f'{time.time()};{self.temp}\n')
                
            if self.press != self.sensor.pressure:
                self.press = self.sensor.pressure
                self.alt = self.sensor.altitude
                with open(self.press_path, 'a') as f:
                    f.write(f'{time.time()};{self.press};{self.alt}\n')
                
            if self.hum != self.sensor.humdidty:
                self.hum = self.sensor.humidity
                with open(self.hum_path, 'a') as f:
                    f.write(f'{time.time()};{self.hum}\n')
            time.sleep(0.199)
                
    
    def setSeaLevelPressure(self, pressure):
        print(pressure)
        self.sensor.sea_level_pressure = pressure

    def getSeaLevelPressure(self):
        return self.sensor.sea_level_pressure

    def getAltitude(self):
        return self.alt

    def getTemp(self):
        return self.temp
    
    def getHum(self):
        return self.hum

    def getPress(self):
        return self.press

class LSM303:
    
    acc: Tuple[float,float,float] = ()
    magvals: Tuple[float,float,float] = ()
    path_mag = 'Data/mag.out'
    path_acc = 'Data/acceleration.out'
    
    def __init__(self, i2c=board.I2C()) ->None:
        self.accel = adafruit_lsm303_accel.LSM303_Accel(i2c)
        self.mag = adafruit_lis2mdl.LIS2MDL(i2c)
        self.mag.data_rate = 3
        self.accel.data_rate = adafruit_lsm303_accel.Rate(5)
        self.rProcess = Process(target=self.refresh)
        self.rProcess.start()
            
    def getAcceleration(self) -> Tuple[float, float, float]:
        return self.acc

    def getMagnetic(self) -> Tuple[float, float, float]:
        return self.magvals

    def refresh(self):
        while True:
            if self.accel.acceleration != self.acc:
                self.acc = self.accel.acceleration
                with open(self.path_acc, 'a')as f:
                    f.write(f'{time.time()};{";".join(map(str, self.acc))}\n')
            
            if self.mag.magnetic != self.magvals:
                self.magvals = self.mag.magnetic
                with open(self.path_acc, 'a')as f:
                    f.write(f'{time.time()};{";".join(map(str, self.magvals))}\n')
            
            time.sleep(0.009)
            
class L76x:
    
    path = 'Data/gps.out'
    
    refresh_delay=1000
    l_rf_time = 0
    gps:L76X.L76X
    def startGPS(self):
        x=L76X.L76X()
        x.L76X_Set_Baudrate(9600)
        x.L76X_Send_Command(x.SET_NMEA_BAUDRATE_115200)
        time.sleep(2)
        x.L76X_Set_Baudrate(115200)
        x.L76X_Send_Command(x.SET_POS_FIX_1S)
        #Set output message
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


    def refresh(self, lat = Value('d', 0), lon = Value('d', 0), fix = Value('i', 0)):
        try:
            self.gps.L76X_Gat_GNRMC()
            self.l_rf_time= time.time()*1000
            lat.value = self.gps.Lat
            lon.value = self.gps.Lon
            fix.value = self.gps.Status
            with open(self.path, 'a')as f:
                f.write(f'{time.time()};{self.gps.Lat};{self.gps.Lon};{self.gps.Status}\n')

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
    temp = -10000
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
            if self.ds18.temperature != self.temp:
                self.temp = self.ds18.temperature
                with open(self.log_path, 'a') as f:
                    f.write(f'{time.time()};{self.temp}\n')
                
            time.sleep(0.125)
    
    def GetTemp(self):
        return self.temp