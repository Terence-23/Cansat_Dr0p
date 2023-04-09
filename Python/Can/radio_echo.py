import adafruit_rfm9x
import digitalio, busio, board

CS = digitalio.DigitalInOut(board.D22)
RESET = digitalio.DigitalInOut(board.D27)
FREQ = 433.6
PWR = 20
SPI = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

radio = adafruit_rfm9x.RFM9x(SPI, CS, RESET, FREQ)
radio.tx_power = PWR

while True:
    in_packet = radio.receive()
    if not in_packet is None:
        radio.send(in_packet)
    
