from main import Servo
import time

servo = Servo()

servo.rotate(servo.neutral)
print('neutral')
time.sleep(10)
servo.rotate(servo.right)
print('right')
time.sleep(10)
servo.rotate(servo.left)
print('left')
time.sleep(10)
servo.rotate(servo.neutral)
print('neutral')
time.sleep(10)
