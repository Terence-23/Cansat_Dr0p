# file for data handling

import time

class Packet:
    @staticmethod
    def now():
        return time.ctime(time.time())
    sep = ';'
    @staticmethod
    def encode(bme, gps, acc):
        gps.refresh()
        packet = f't{Packet.now()}{Packet.sep}a{gps.getLat()}{Packet.sep}o{gps.getLon()}{Packet.sep}g{acc.getAcceleration()}{Packet.sep}m{acc.getMagnetic}{Packet.sep}T{bme.getTemp()}{Packet.sep}H{bme.getHum()}{Packet.sep}P{bme.getPress()}'
        return packet
    @staticmethod
    def decode(packet:str):
        data = packet.split(sep=Packet.sep)
        for i in data:
            # expected GPS lat
            if i[0] == 'a':

                pass
            # expected GPS lon
            elif i[0] == 'o':
                pass
            # confirm recieving
            elif i[0] =='h':
                Radio.send_packet("c")
            # ignore c
            elif i[0] == 'c':
                pass
            elif i[0] == 't':
                # timestamp
                pass
            elif i[0] == 'g':
                # acceleration
                # (x, y, z)
                pass
            elif i[0] == 'm':
                # Magnetic
                # (x, y, z)
                pass
            elif i[0] == 'T':
                # temp
                pass
            elif i[0] == 'H':
                # humidity
                pass
            elif i[0] == 'P':
                # pressure
                pass

            else:
                SD_o.write(f"Unknown packet ID: {i[0]}")
        
                    
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
        self.rfm9x.send(bytes(msg, "ascii"))
    def recv(self, delay = 0.5):
        return self.rfm9x.receive(delay)
    


SD_o:SD