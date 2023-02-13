#!/bin/python3
import comms, sensor
import time
import board, digitalio
import new_Packet

def init():
    global lsm, bme, gps, radio, pitch, roll, desiredPos
    desiredPos = (0,0)
    # lsm = sensor.LSM303()
    bme = sensor.BME(i2c=board.I2C())
    comms.SD_o = comms.SD('log.out')
    sensor.SD_o = comms.SD_o
    # gps = sensor.L76x()
    radio = comms.Radio(comms.CS, comms.RESET, comms.PWR, comms.FREQ)
    # time.sleep(15)
    # pitch, roll = calculate_angles(*lsm.getAcceleration())
    # time.sleep(4)
    # lsm.mag = calibrate(lsm.mag)
    # servo = Servo()


def update():
    with open("/home/pi/Cansat/Python/batteryTest.log", 'a') as f:
        f.write('update\n')
        # gps.refresh()
        packet = new_Packet.Packet.create_base_packet(time.time(), bme.getTemp(), bme.getPress(), bme.getHum(), bme.getAltitude())
        radio.send(packet.encode())
        comms.SD_o.write(packet.to_json())
        _in = radio.recv()
        
        print(_in)
        try:
            packet = new_Packet.Packet.decode(_in)
            print(packet.to_json())
            
        except Exception:
            print('could not decode packet')
        
        # comms.SD_o.write(_in)
        # packet = comms.Packet()
        # packet.decode(_in)
        # bme.setSeaLevelPressure(packet.pressure if packet.pressure != '' else bme.getSeaLevelPressure())
        f.write('updateEnd \n')
    # desiredPos = packet.gps_position if packet.gps_position != '' else desiredPos
    # nav(Packet)


def main():
    try:
        init()
        while 1:
            update()
    except Exception as e:
        with open('log.out') as f:
            f.write(f"Exception: {e}")

if __name__ =="__main__":
    main()
