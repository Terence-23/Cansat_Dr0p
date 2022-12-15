#!/bin/python3
import comms, sensor
import time

def nav():
    pass

def init():
    global lsm, bme, gps 
    lsm = sensor.LSM303()

    bme = sensor.BME()
    comms.SD_o = comms.SD('log.out')
    gps = sensor.L76x()

def update():
    gps.refresh()
    packet = comms.Packet.encode(bme, gps, lsm)
    comms.Radio.send_packet(packet)
    comms.SD_o.write(packet)
    _in = comms.Radio.recv_packet()
    comms.Packet.decode(_in)
    nav()

def main():
    init()
    while 1:
        update()

    while 1:
        time.sleep(1)
        print(f"Acceleration(m/s^2) {lsm.getAcceleration()}\n Magnetic(uTeslas){lsm.getMagnetic()}")


if __name__ =="__main__":
    main()
