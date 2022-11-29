# file for sensor communication


# bme
# import adafruit_bme680

import time
from lib.L76x import L76X
# import math
import comms
from time import ctime
import board
import digitalio
import adafruit_bme680

SD_o:comms.SD


class BME:
    sensor:adafruit_bme680.Adafruit_BME680
    def __init__(self, cs = digitalio.DigitalInOut(board.D22), spi = board.SPI()) -> None:
        self.sensor = adafruit_bme680.Adafruit_BME680_SPI(spi, cs)
    
    def getTemp(self):
        return self.sensor.temperature
    
    def getHum(self):
        return self.sensor.humidity

    def getPress(self):
        return self.sensor.pressure

class L76x:
    
    refresh_delay=1000
    l_rf_time = 0
    gps:L76X.L76X
    
    def __init__(self):
        try:
            x=L76X.L76X()
            x.L76X_Set_Baudrate(9600)
            x.L76X_Send_Command(x.SET_NMEA_BAUDRATE_115200)
            time.sleep(2)
            x.L76X_Set_Baudrate(115200)
            x.L76X_Send_Command(x.SET_POS_FIX_400MS)
            #Set output message
            x.L76X_Send_Command(x.SET_NMEA_OUTPUT)
            x.L76X_Exit_BackupMode()
            self.gps = x
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            SD_o.write(f'{e}')


    def refresh(self):
        try:
            self.gps.L76X_Gat_GNRMC()
            self.l_rf_time= time.time()*1000

        except KeyboardInterrupt as e:
            raise e

        except Exception as e:
            SD_o.write(f'{e}')

    def getLat(self):
        # if self.l_rf_time + self.refresh_delay <= time.time() * 1000: self.refresh()
        
        return self.gps.Lat
    
    def hasFix(self):
        # if self.l_rf_time + self.refresh_delay <= time.time() * 1000: self.refresh()
        return self.gps.Status == 1
    
    def getLon(self):
        # if self.l_rf_time + self.refresh_delay <= time.time() * 1000: self.refresh()
        return self.gps.Lon

