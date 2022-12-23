# file for data handling
from ast import literal_eval as l_eval

import time
import digitalio, board
import busio, adafruit_rfm9x

class Packet:
    def __init__(self, timestamp='', temperature='', pressure='', humidity='', gps_position='', acceleration='', magnetometer_reading='', altitude=''):
        self.timestamp = timestamp
        self.temperature = temperature
        self.pressure = pressure
        self.humidity = humidity
        self.gps_position = gps_position
        self.acceleration = acceleration
        self.magnetometer_reading = magnetometer_reading
        self.altitude = altitude
        
    def encode(self):
        # Encode the packet into a string
        packet_string = str(self.timestamp) + ";" + str(self.temperature) + ";" + str(self.pressure) + ";"
        packet_string += str(self.humidity) + ";" + str(self.gps_position) + ";" + str(self.acceleration) + ";"
        packet_string += str(self.magnetometer_reading) + ';' + str(self.altitude)
        return packet_string
    
    def decode(self, bytestream):
        # Decode the bytestream and update the packet's attributes
        if bytestream == None:
            SD_o.write("No data to decode")
            return
        packet_string = str(bytestream).strip()
        packet_parts = packet_string.split(";")

		# assigning values from packet
        if packet_parts[0] != '':
            self.timestamp = packet_parts[0]
        if packet_parts[1] != '':
            self.temperature = float(packet_parts[1])
        if packet_parts[2] != '':
            self.pressure = float(packet_parts[2])
        if packet_parts[3] != '':
            self.humidity = float(packet_parts[3])
        if packet_parts[4] != '':
            self.gps_position = l_eval(packet_parts[4])
        if packet_parts[5] != '':
            self.acceleration = l_eval(packet_parts[5])
        if packet_parts[6] != '':
            self.magnetometer_reading = l_eval(packet_parts[6])
        if packet_parts[7] != '':
            self.altitude = float(packet_parts[7])

    def __str__(self) -> str:
        return f"Packet({self.timestamp},{self.temperature},{self.pressure},{self.humidity},\
            {self.gps_position},{self.acceleration},{self.magnetometer_reading},{self.altitude})"

                    
class SD:
    # get path to log file
    def __init__(self, f_name) -> None:
        self.f_name = f_name

    def write(self, packet):
        with open(self.f_name, 'a', encoding="utf-8") as f:
            # write the packet with a timestamp
            f.write(f"{time.ctime()} :: {packet}\n")
    
CS = digitalio.DigitalInOut(board.D22)
RESET = digitalio.DigitalInOut(board.D27)
FREQ = 433.0
PWR = 20

class Radio:
    def __init__(self, cs, rst, power, freq, spi=busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)):
        self.cs = cs
        self.rst = rst
        self.power = power
        self.freq = freq

        self.rfm9x = adafruit_rfm9x.RFM9x(spi, cs, rst, freq)
        self.rfm9x.tx_power = power
    def send(self, msg:str):
        self.rfm9x.send(bytes(str(msg), "ascii"))
    def recv(self, timeout = 0.5):
        return self.rfm9x.receive(timeout=timeout)
    


SD_o:SD