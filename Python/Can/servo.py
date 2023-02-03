from main import Servo
import time

servo = Servo()

servo.rotate(servo.neutral)
print('neutral')
time.sleep(10)
