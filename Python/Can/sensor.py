# file for sensor communication


# bme
# import adafruit_bme680

import time
from lib.L76x import L76X
import math
import board
import digitalio
import adafruit_bme680


class BME:
    def __init__(self, cs = digitalio.DigitalInOut(board.D22), spi = board.SPI()) -> None:
        self.sensor = adafruit_bme680.Adafruit_BME680_SPI(spi, cs)
    
    def getTemp(self):
        return sensor.temperature
    
    def getHum(self):
        return sensor.humidity

    def getPress(self):
        return sensor.pressure

class L76X:
    def __init__(self):
        # try:
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

    def getLat(self):
        return self.gps.Lat
    def getLon(self):
        return self.gps.Lon

