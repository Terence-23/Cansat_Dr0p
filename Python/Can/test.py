from ast import literal_eval as l_eval

class Packet:
    def __init__(self, timestamp, temperature, pressure, humidity, gps_position, acceleration, magnetometer_reading):
        self.timestamp = timestamp
        self.temperature = temperature
        self.pressure = pressure
        self.humidity = humidity
        self.gps_position = gps_position
        self.acceleration = acceleration
        self.magnetometer_reading = magnetometer_reading
        
    def encode(self):
        # Encode the packet into a string
        packet_string = str(self.timestamp) + "," + str(self.temperature) + "," + str(self.pressure) + ","
        packet_string += str(self.humidity) + "," + str(self.gps_position) + "," + str(self.acceleration) + ","
        packet_string += str(self.magnetometer_reading)
        return packet_string
    
    def decode(self, bytestream):
        # Decode the bytestream and update the packet's attributes
        packet_string = bytestream.strip()
        packet_parts = packet_string.split(",")

		# assigning values from packet
        self.timestamp = packet_parts[0]
        self.temperature = float(packet_parts[1])
        self.pressure = float(packet_parts[2])
        self.humidity = float(packet_parts[3])
        self.gps_position = l_eval(packet_parts[4])
        self.acceleration = l_eval(packet_parts[5])
        self.magnetometer_reading = l_eval(packet_parts[6])
