from enum import Enum
import json
import time

class PacketType(Enum):
    COMMAND = 'c'
    BASE = 'b'
    EXTENDED = 'e'

class Command(Enum):
    SLEEP = 'sleep'
    WAKE = 'wake'
    SETPOS = 'setPos'
    SETPRESS = 'setPress'


class Packet:
    def __eq__(self, other):
        if isinstance(other, Packet):
            return self.payload == other.payload and \
                self.timestamp == other.timestamp and\
                self.packet_type == other.packet_type
        
        elif isinstance(other, str):
            other = Packet.decode(other)
            return self.payload == other.payload and \
                self.timestamp == other.timestamp and\
                self.packet_type == other.packet_type
        
        return False
    
    def __init__(self, packet_type, timestamp, payload):
        self.packet_type = packet_type
        self.timestamp = timestamp
        self.payload = payload
        
    @classmethod
    def decode(cls, string):
        packet_type, timestamp, *payload = string.split(';')
        packet_type = PacketType(packet_type)
        
        timestamp = float(timestamp)
        
        if packet_type == PacketType.COMMAND:
            command, *args = payload
            command = Command(command)
            if args != ['None']:
                args = [float(arg) for arg in args]
            else:
                args = None
            payload = {'command': command, 'args': args}
        
        elif packet_type == PacketType.BASE:
            temp, pressure, humidity, altitude = map(float, payload)
            payload = {'temp': temp, 'pressure': pressure, 'humidity': humidity, 'altitude': altitude}
        
        elif packet_type == PacketType.EXTENDED:
            gps_lat, gps_lon, ax, ay, az, mx, my, mz = map(float, payload)
            payload = {'lat': gps_lat, 'lon':gps_lon, 'acceleration_x': ax, 'acceleration_y': ay, 'acceleration_z': az, 'magnetometer_x': mx, 'magnetometer_y': my, 'magnetometer_z': mz}
        
        return cls(packet_type, timestamp, payload)
    
    def encode(self):
        packet_type = self.packet_type.value
        timestamp = str(self.timestamp)
        if self.packet_type == PacketType.COMMAND:
            command, args = self.payload.values()
            args = str(args)
            payload = f'{command.value};{args}'
        elif self.packet_type == PacketType.BASE:
            temp, pressure, humidity, altitude = self.payload.values()
            payload = ';'.join(map(str, (temp, pressure, humidity, altitude)))
        elif self.packet_type == PacketType.EXTENDED:
            gps_lat, gps_lon, ax, ay, az, mx, my, mz = self.payload.values()
            payload = ';'.join(map(str, (gps_lat, gps_lon, ax, ay, az, mx, my, mz)))
        return f'{packet_type};{timestamp};{payload}'
    
    def to_json(self):
        data = {k: str(v) for k, v in self.payload.items()}
        return json.dumps({
            'packet_type': self.packet_type.value,
            'timestamp': self.timestamp,
            'payload': data
        })
    
    @staticmethod    
    def create_command_packet(timestamp, command, args=None):
        if not type(command) == Command:
            command = Command(command)
        return Packet(PacketType.COMMAND, timestamp, {'command': command, 'args': args})

    @staticmethod
    def create_base_packet(timestamp, temp, pressure, humidity, altitude):
        return Packet(PacketType.BASE, timestamp, {'temp': temp, 'pressure': pressure, 'humidity': humidity, 'altitude': altitude})

    @staticmethod
    def create_extended_packet(timestamp, lat, lon, acceleration_x, acceleration_y, acceleration_z, magnetometer_x, magnetometer_y, magnetometer_z):
            return Packet(PacketType.EXTENDED, timestamp, {'lat': lat, 'lon':lon, 'acceleration_x': acceleration_x, 'acceleration_y': acceleration_y, 'acceleration_z': acceleration_z, 'magnetometer_x': magnetometer_x, 'magnetometer_y': magnetometer_y, 'magnetometer_z': magnetometer_z})


def main():
    com_packet = Packet.create_command_packet(time.time(), Command.SLEEP)
    base_packet = Packet.create_base_packet(time.time(), 10, 1013, 40, 100)
    ext_packet = Packet.create_extended_packet(time.time(),50, 20, 0, 9.8, 0, 0, 0 ,0)

    assert com_packet.encode() == com_packet
    assert base_packet.encode() == base_packet
    assert ext_packet.encode() == ext_packet

    print(base_packet.to_json())


if __name__ == "__main__":
    main()