#!/bin/python3
import comms, sensor
import time
import board, digitalio


def init():
    global lsm, bme, gps, radio, pitch, roll, desiredPos
    desiredPos = (0,0)
    # lsm = sensor.LSM303()
    bme = sensor.BME(i2c=board.I2C())
    comms.SD_o = comms.SD('log.out')
    sensor.SD_o = comms.SD_o
    # gps = sensor.L76x()
    radio = comms.Radio(comms.CS, comms.RESET, comms.PWR, comms.FREQ)
    time.sleep(15)
    # pitch, roll = calculate_angles(*lsm.getAcceleration())
    time.sleep(4)
    # lsm.mag = calibrate(lsm.mag)
    # servo = Servo()


def update():
    # gps.refresh()
    Packet = comms.Packet(time.ctime(), temperature=bme.getTemp(), pressure=bme.getPress(), humidity=bme.getHum(), gps_position=None,\
         acceleration= None, magnetometer_reading= None, altitude=bme.getAltitude())

    packet = Packet.encode()
    radio.send(packet)
    comms.SD_o.write(packet)
    _in = radio.recv()
    comms.SD_o.write(_in)
    packet = comms.Packet()
    packet.decode(_in)
    bme.setSeaLevelPressure(packet.pressure if packet.pressure != '' else bme.getSeaLevelPressure())
    # desiredPos = packet.gps_position if packet.gps_position != '' else desiredPos
    # nav(Packet)


def main():
    init()
    while 1:
        update()


if __name__ =="__main__":
    main()
