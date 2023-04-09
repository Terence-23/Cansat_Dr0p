import adafruit_rfm9x
import digitalio, busio, board
import time, traceback
from new_Packet import Packet, PacketType, Command

CS = digitalio.DigitalInOut(board.D22)
RESET = digitalio.DigitalInOut(board.D27)
FREQ = 433.6
PWR = 20
SPI = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

radio = adafruit_rfm9x.RFM9x(SPI, CS, RESET, FREQ)
radio.tx_power = PWR

same = 0
diff = 0
try:
    while True:
        data = 1    
        packet = bytearray(str(Packet.create_base_packet(time.time(), 20, 1013, 30, 0)),'ascii')
        radio.send(packet)
        
        echod = radio.receive()
        print('\n', packet)
        print(echod)
        
        if echod is None:
            continue
        elif echod == packet:
            same +=1
        else:
            diff +=1
except:
    traceback.print_exc()
finally:
    print(f'Same:{same}, Different:{diff}, Ratio:{same/diff}')
    