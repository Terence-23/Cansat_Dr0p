#!/bin/python3
import comms, sensor
import time
import board, digitalio

def nav(packet: comms.Packet):
    # placeholder
    print(packet)


def init():
    global lsm, bme, gps, radio
    lsm = sensor.LSM303()
    bme = sensor.BME(i2c=board.I2C())
    comms.SD_o = comms.SD('log.out')
    sensor.SD_o = comms.SD_o
    gps = sensor.L76x()
    radio = comms.Radio(comms.CS, comms.RESET, comms.PWR, comms.FREQ)

def update():
    gps.refresh()
    Packet = comms.Packet(time.ctime(), temperature=bme.getTemp(), pressure=bme.getPress(), humidity=bme.getHum(), gps_position=(gps.getLat(), gps.getLon()),\
         acceleration= lsm.getAcceleration(), magnetometer_reading= lsm.getMagnetic(), altitude=bme.getAltitude())

    packet = Packet.encode()
    radio.send(packet)
    comms.SD_o.write(packet)
    _in = radio.recv()
    comms.SD_o.write(_in)
    Packet.decode(_in)
    nav(Packet)

def main():
    init()
    while 1:
        update()



if __name__ =="__main__":
    main()
