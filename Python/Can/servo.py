#!/bin/python3

from psteering import Servo
import time
import multiprocessing as mp

servo = Servo()

def target(servo):
    servo.rotate(80.0)
    print('left')
    time.sleep(5)
    servo.rotate(45.5)
    print('right')
    time.sleep(5)
    servo.rotate(69.9348236725378587)
    print('neutral')
    time.sleep(5)
    
steer_p = mp.Process(target=target, args=(servo,))

steer_p.start()
steer_p.join()

print('main_p')
servo.rotate(80.0)
print('left')
time.sleep(5)
servo.rotate(45.5)
print('right')
time.sleep(5)
servo.rotate(69.9348236725378587)
print('neutral')
time.sleep(5)
