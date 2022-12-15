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
    

class Radio:
    
    @staticmethod
    def send_packet(packet:str):
        # placeholder
        print(packet)
        pass
    
    @staticmethod
    def recv_packet() ->str:
        packet:str = ''

        return packet


SD_o:SD