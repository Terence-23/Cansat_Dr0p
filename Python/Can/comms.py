# file for data handling
from ast import literal_eval as l_eval
import traceback

import time
import digitalio, board
import busio, adafruit_rfm9x

FL_PACKET="PACKET"
FL_STEER="STEERING"
FL_GPS="GPS"
FL_ERROR="ERROR"
FL_DEBUG="DEBUG"

class Packet:
    def __init__(self, timestamp=None, temperature=None, pressure=None, humidity=None, gps_position=None, acceleration=None, magnetometer_reading=None, altitude=None):
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
        packet_string = ';'+ str(self.timestamp) + ";" + str(self.temperature) + ";" + str(self.pressure) + ";"
        packet_string += str(self.humidity) + ";" + str(self.gps_position) + ";" + str(self.acceleration) + ";"
        packet_string += str(self.magnetometer_reading) + ';' + str(self.altitude) + ';'
        SD_o.write(FL_DEBUG, len(packet_string))
        print(len(packet_string))
        return packet_string
    
    def decode(self, bytestream):
        # Decode the bytestream and update the packet's attributes
        if bytestream == None:
            SD_o.write(FL_ERROR, "No data to decode")
            return
        packet_string = str(bytestream).strip()
        packet_parts = packet_string.split(";")[1:-1]
        print(packet_parts)

        try: 
            if len(packet_parts) != 8:
                raise ValueError("Invalid Packet")
        except ValueError as e:
            SD_o.write(FL_ERROR, traceback.format_exc())
            return False

		# assigning values from packet
        if packet_parts[0] != 'None':
            self.timestamp = packet_parts[0]
        if packet_parts[1] != 'None':
            self.temperature = float(packet_parts[1])
        if packet_parts[2] != 'None':
            self.pressure = float(packet_parts[2])
        if packet_parts[3] != 'None':
            self.humidity = float(packet_parts[3])
        if packet_parts[4] != 'None':
            self.gps_position = l_eval(packet_parts[4])
        if packet_parts[5] != 'None':
            self.acceleration = l_eval(packet_parts[5])
        if packet_parts[6] != 'None':
            self.magnetometer_reading = l_eval(packet_parts[6])
        if packet_parts[7] != 'None':
            self.altitude = float(packet_parts[7])

    def __str__(self) -> str:
        return f"Packet({self.timestamp},{self.temperature},{self.pressure},{self.humidity},\
            {self.gps_position},{self.acceleration},{self.magnetometer_reading},{self.altitude})"

                    
class SD:
    # get path to log file
    def __init__(self, f_name) -> None:
        self.f_name = f_name

    def write(self, flag, packet):
        with open(self.f_name, 'a', encoding="utf-8") as f:
            # write the packet with a timestamp
            f.write(f"{time.ctime()}::{flag}::{packet}\n")
    
CS = digitalio.DigitalInOut(board.D22)
RESET = digitalio.DigitalInOut(board.D27)
FREQ = 433
PWR = 20

class Radio:
    def __init__(self, cs=CS, rst=RESET, power=PWR, freq=FREQ, spi=busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)):
        self.cs = cs
        self.rst = rst
        self.power = power
        self.freq = freq

        self.rfm9x = adafruit_rfm9x.RFM9x(spi, cs, rst, freq)
        self.rfm9x.tx_power = power
        
    def send(self, msg:str):
        self.rfm9x.send_with_ack(bytes(str(msg), "ascii"))
        
    def recv(self, timeout = 0.5, with_ack=False):
        packet = self.rfm9x.receive(timeout=timeout, with_ack=with_ack)
        if packet is None:
            print("no packet")
            return None
        else:
            print("packet")
            SD_o.write(FL_DEBUG, f"RSSI:{self.rfm9x.last_rssi}")
            return str(packet, 'ascii')
    


SD_o:SD
