from new_main import Servo
import time

servo = Servo()

servo.rotate(servo.left)
print('left')
time.sleep(5)
servo.rotate(servo.right)
print('right')
time.sleep(5)
servo.rotate(servo.neutral)
print('neutral')
time.sleep(5)
