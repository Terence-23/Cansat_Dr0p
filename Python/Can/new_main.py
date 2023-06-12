#!/bin/python3
from typing import Tuple
import comms
import sensor
from new_Packet import Packet, PacketType, Command
from ast import literal_eval as l_eval
import numpy as np
import time
import board
import digitalio
import threading
import math
import traceback
from multiprocessing import Process, Value, Queue
from psteering import steer_target, Servo


def acceleration_wake(acceleration, accel: sensor.LSM303()):
    accel = accel.getAcceleration()
    return np.sqrt(accel[0] ** 2 + accel[1] ** 2 + accel[2] ** 2) > acceleration


event_q = Queue()
send_q = Queue()


def wake_check(lsm, bme):

    print('wake check')
    g = 9.82
    alt = 50
    acc = 3*g

    check_fs = [(acceleration_wake, acc, lsm), (lambda alt,
                                                bme: bme.getAltitude() > alt, alt, bme)]

    for i, (v, *args) in enumerate(check_fs):
        print(f"{i} {v.__name__} {args}")
        print(v(*args))

        comms.SD_o.write('WAKE', f'{v.__name__}: {v(*args)}')
        comms.SD_o.write('WAKE', f'{bme.getPress()}')
        if v(*args):
            print('wake')
            return True

    print('sleep')
    return False


def wake_checker(lsm, bme, sleeping):
    print('start wake checker')
    while True:
        time .sleep(0.1)
        print(sleeping.value, 'sleeping')
        if sleeping.value and wake_check(lsm, bme):
            comms.SD_o.write(comms.FL_DEBUG, 'auto_wake')
            packet = Packet.create_command_packet(time.time(), Command.WAKE)
            event_q.put(packet.encode())


def radio_recv(radio):
    while True:
        while not send_q.empty():
            try:
                radio.send(send_q.get(block=False))
            except:
                pass

        text = radio.recv(with_ack=True)
        if not text is None:
            event_q.put(text)


def gps_refresh(lat, lon, gpsFix, runCount):
    gps = sensor.L76x()
    print('after gps init')

    while True:
        runCount.value += 1
        gps.refresh(lat, lon, gpsFix)


isturning = False


def main():
    global isturning
    # init
    sleeping = Value('i', 1)
    # turn_delay = 1
    wake_cycle = 0.5 # seconds
    # last_rotate = time.time() - turn_delay
    e = 10

    comms.SD_o = comms.SD('Data/log.out')
    sensor.SD_o = comms.SD_o

    lat = Value('d', 0.0)
    lon = Value('d', 0.0)
    gpsFix = Value('i', 0)
    runCount = Value('i', 0)

    desiredPos = Value('d', 52.2449603), Value('d',21.8641596)

    dallas = sensor.Dallas()
    lsm = sensor.LSM303()
    bme = sensor.BME(i2c=board.I2C())
    bme.setSeaLevelPressure(bme.getPress())
    radio = comms.Radio(comms.CS, comms.RESET, comms.PWR, comms.FREQ)

    gps_p = Process(target=gps_refresh, args=(lat, lon, gpsFix, runCount,))
    gps_p.start()

    radio_p = Process(target=radio_recv, args=(radio,))
    radio_p.start()

    wake_p = Process(target=wake_checker, args=(lsm, bme, sleeping,))
    wake_p.start()
    
    # left, right, neutral, max_t, servo, lsm, gps
    servo = Servo()
    servo_rot = Value('d', servo.neutral)
    steer_p = Process(target=steer_target, args=(Servo.left, Servo.right, Servo.neutral, 60, lsm, [lat,lon], desiredPos, sleeping, servo_rot,))
    steer_p.start()

    time.sleep(0)
    # hardiron_calibration = calibrate()
    c_press = bme.getPress()
    sleep_time = time.monotonic()
    sleep_delay = 600

    print('freq', radio.rfm9x.frequency_mhz)

    while 1:
        print(runCount.value)
        # send basic packet
        comms.SD_o.write(comms.FL_DEBUG, f"alt: {bme.getAltitude()}, sea: {bme.getSeaLevelPressure()}")
        packet_b = Packet.create_base_packet(
            time.time(), dallas.temp.value, bme.getPress(), bme.getHum(), bme.getAltitude())

        comms.SD_o.write(comms.FL_PACKET, packet_b.to_json())
        print(packet_b.to_json())
        try:
            send_q.put_nowait(packet_b.encode())
        except:
            comms.SD_o.write(comms.FL_ERROR, 'send queue is full')

        # deal with all incoming packets
        while not event_q.empty():
            print('event_q not empty')
            in_text = event_q.get(block=False)
            if not in_text is None:
                print(in_text)
                try:
                    in_packet = Packet.decode(in_text)
                    comms.SD_o.write(comms.FL_PACKET, in_packet.to_json())
                    if in_packet.packet_type == PacketType.COMMAND:
                        command = in_packet.payload['command']
                        if command == Command.SLEEP:
                            sleeping.value = 1
                        elif command == Command.WAKE:
                            sleeping.value = 0
                            c_press = bme.getPress()
                            sleep_time = time.monotonic()
                        elif command == Command.SETPOS:
                            desiredPos[0].value = in_packet.payload['args'][0]
                            desiredPos[1].value = in_packet.payload['args'][1]
                            comms.SD_o.write(comms.FL_DEBUG, desiredPos)
                        elif command == Command.SETPRESS:
                            bme.setSeaLevelPressure(
                                in_packet.payload['args'][0])
                            comms.SD_o.write(
                                comms.FL_DEBUG, bme.getSeaLevelPressure())
                        else:
                            comms.SD_o.write(comms.FL_ERROR,
                                             "Invalid command in Packet: {}".format(in_packet.to_json()))
                    else:
                        comms.SD_o.write(comms.FL_ERROR,
                                         "Packet not a command: {}".format(in_packet.to_json()))

                except KeyboardInterrupt as e:
                    raise e

                except Exception as e:
                    comms.SD_o.write(comms.FL_ERROR, traceback.format_exc())
                    traceback.print_exc()

            else:
                comms.SD_o.write(comms.FL_PACKET, 'no Packet recieved')

        if sleeping.value == 1:
            print('sleeping')

            time.sleep(0.5)
        else:
            print(c_press, not (c_press + 1 > bme.getPress()
                  > c_press - 1), bme.getPress(), sep=' ')
            # go to sleep
            if not c_press + 2 > bme.getPress() > c_press - 2:
                c_press = bme.getPress()
                sleep_time = time.monotonic()
                # raise Exception('delay')
            elif time.monotonic() > sleep_time + sleep_delay:
                sleeping.value = 1
                # raise Exception('sleep')

            print(gpsFix.value)
            # send extended packet
            packet_e = Packet.create_extended_packet(math.floor(
                time.time()), lat.value, lon.value, *lsm.getAcceleration(), *lsm.getMagnetic())

            try:
                send_q.put_nowait(packet_e.encode())
            except:
                comms.SD_o.write(comms.FL_ERROR, 'send queue is full')
            print(packet_e.to_json())
            comms.SD_o.write(comms.FL_PACKET, packet_e.to_json())

            for i in range(int(wake_cycle * 10)):
                servo.rotate(servo_rot.value)
                print(f'servo rot: {servo_rot.value}')
                time.sleep(.1)
            
            # pitch, roll = calculate_angles(*lsm.getAcceleration())

            # # steer
            # print(f"isturning: {isturning}")
            # if isturning:
            #     continue
            # isturning = True
            # print("Turning")
            # # last_rotate = time.time()

            # mag_corected = normalize(
            #     np.array(lsm.getMagnetic()), hardiron_calibration)
            # compass = compass_reading(*mag_corected)
            # rotation = get_rotation((lat.value, lon.value), desiredPos)
            # rotation_to_do = get_rotation_difference(compass, rotation)

            # print(
            #     f"compass: {compass}, rotation: {rotation}, get_rotation_difference: {rotation_to_do}")

            # if rotation_to_do < -e:
            #     print(isturning)
            #     # go Left
            #     comms.SD_o.write(comms.FL_STEER, 'left')
            #     def repeat_function():
            #         global isturning
            #         print(isturning)
            #         # replace function with function to rotate servo by 45 degrees
            #         print('go left')
            #         servo.rotate(servo.left)
            #         start = time.time()
            #         # des_rotation = get_rotation((lat, lon), desiredPos)
            #         while get_rotation_difference(compass_reading(*normalize(np.array(lsm.getMagnetic()),
            #                                                                  hardiron_calibration)), rotation) < -e and time.time() < start + turn_delay:
            #             # Add a delay if necessary
            #             # print(get_rotation_difference(compass_reading(*normalize(np.array(lsm.getMagnetic()), hardiron_calibration)),rotation))
            #             time.sleep(0.020)

            #         if not get_rotation_difference(compass_reading(*normalize(np.array(lsm.getMagnetic()),
            #                                                                   hardiron_calibration)), rotation) < -e:
            #             servo.rotate(servo.neutral)
            #             print("neutral left")
            #         isturning = False

            # elif rotation_to_do > e:
            #     # go Right
            #     comms.SD_o.write(comms.FL_STEER, 'right')
            #     def repeat_function():
            #         global isturning
            #         # replace function with function to rotate servo by 45 degrees
            #         print(servo.right)
            #         servo.rotate(servo.right)

            #         print('go right')
            #         start = time.time()
            #         # des_rotation = get_rotation(
            #         #    (lat, lon), desiredPos)
            #         while get_rotation_difference(compass_reading(*normalize(np.array(lsm.getMagnetic()),
            #                                                                  hardiron_calibration)), rotation) > e and time.time() < \
            #                 start + turn_delay:
            #             # print(get_rotation_difference(compass_reading(*normalize(np.array(lsm.getMagnetic()), hardiron_calibration)),rotation))
            #             # Add a delay if necessary
            #             time.sleep(0.020)

            #         if not get_rotation_difference(compass_reading(*normalize(np.array(lsm.getMagnetic()),
            #                                                                   hardiron_calibration)), rotation) > e:
            #             servo.rotate(servo.neutral)
            #             print("neutral right")
            #         isturning = False

            # else:
            #     comms.SD_o.write(comms.FL_STEER, 'neutral')
            #     def repeat_function():
            #         global isturning
            #         print('neutral')
            #         servo.rotate(servo.neutral)
            #         isturning = False

            # repeat_function()


if __name__ == '__main__':
    main()
