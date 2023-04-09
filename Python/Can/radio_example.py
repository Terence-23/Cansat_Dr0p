#!/bin/python

import board
import busio
import digitalio
import time
import traceback

import adafruit_rfm9x
from new_Packet import Packet, PacketType, Command


RADIO_FREQ_MHZ = 433.0  # Frequency of the radio in Mhz. Must match your

CS = digitalio.DigitalInOut(board.D22)
RESET = digitalio.DigitalInOut(board.D27)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

rfm9x.tx_power = 20


while True:
  try:
    rfm9x.send(bytes(str(Packet.create_base_packet(time.time(), 30, 1013,40,0)), "ascii"))
    print("Sent Hello World message!")

    print("Waiting for packets...")

    packet = rfm9x.receive()
    if packet is None:
        print("Received nothing! Listening again...")
    else:
        print("Received (raw bytes): {0}".format(packet))
        with open('log.out', 'a') as f:
            f.write(f"{packet}")
        rssi = rfm9x.last_rssi
        print("Received signal strength: {0} dB".format(rssi))
  except Exception as e:
    traceback.print_exc()  
