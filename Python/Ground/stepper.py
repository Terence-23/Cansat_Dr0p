# SPDX-FileCopyrightText: 2019 Mikey Sklar for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time
import board
import digitalio
import math

class Stepper:
    reverse = False
    
    def __init__(self, steps_per_circle = 200, delay = 1, 
                 en=digitalio.DigitalInOut(board.D18), 
                 step_pin=digitalio.DigitalInOut(board.D4), 
                 dir_pin=digitalio.DigitalInOut(board.D17)
                 ) -> None:
        self.delay = delay
        self.steps = steps_per_circle
        
        self.enable_pin = en
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        
        self.enable_pin.direction = digitalio.Direction.OUTPUT
        self.step_pin.direction = digitalio.Direction.OUTPUT
        self.dir_pin.direction = digitalio.Direction.OUTPUT
        
        self.enable_pin.value = False
    
    def rotate(self, angle, degrees=False):
        if degrees:
            angle = math.radians(angle)
        steps_to_do = self.steps * angle // (2 * math.pi)
        
        if self.reverse:
            steps_to_do *= -1
        
        if steps_to_do > 0:
            self.forward(steps_to_do)
        
        elif steps_to_do < 0:
            self.backwards(steps_to_do)     
    
    def forward(self, steps):
        self.dir_pin = 0
        delay = self.delay
        for _ in range(steps):
            self.step_pin.value =1
            time.sleep(delay)
            self.step_pin.value = 0
            time.sleep(delay)

    def backwards(self, steps):
        self.dir_pin = 1
        delay = self.delay
        for _ in range(steps):
            self.step_pin.value =1
            time.sleep(delay)
            self.step_pin.value = 0
            time.sleep(delay)

    def setStep(self, w1, w2, w3, w4):
        self.coil_A_1_pin.value = w1
        self.coil_A_2_pin.value = w2
        self.coil_B_1_pin.value = w3
        self.coil_B_2_pin.value = w4
        
        
class StepperH:
    reverse = False
    
    def __init__(self, steps_per_circle = 200, delay = 1, 
                 en=digitalio.DigitalInOut(board.D18), 
                 A1=digitalio.DigitalInOut(board.D4), 
                 A2=digitalio.DigitalInOut(board.D17), 
                 B1=digitalio.DigitalInOut(board.D23), 
                 B2=digitalio.DigitalInOut(board.D24)) -> None:
        self.delay = delay
        self.steps = steps_per_circle
        
        self.enable_pin = en
        self.coil_A_1_pin = A1
        self.coil_A_2_pin = A2
        self.coil_B_1_pin = B1
        self.coil_B_2_pin = B2

        self.enable_pin.direction = digitalio.Direction.OUTPUT
        self.coil_A_1_pin.direction = digitalio.Direction.OUTPUT
        self.coil_A_2_pin.direction = digitalio.Direction.OUTPUT
        self.coil_B_1_pin.direction = digitalio.Direction.OUTPUT
        self.coil_B_2_pin.direction = digitalio.Direction.OUTPUT
        
        
        self.enable_pin.value = True
    
    def rotate(self, angle, degrees=False):
        if degrees:
            angle = math.radians(angle)
        steps_to_do = self.steps * angle // 2* math.pi
        
        if self.reverse:
            steps_to_do *= -1
        
        if steps_to_do > 0:
            self.forward(steps_to_do)
        
        elif steps_to_do < 0:
            self.backwards(steps_to_do)     
    
    def forward(self, steps):
        i = 0
        delay = self.delay
        while i in range(0, steps):
            self.setStep(1, 0, 1, 0)
            time.sleep(delay)
            self.setStep(0, 1, 1, 0)
            time.sleep(delay)
            self.setStep(0, 1, 0, 1)
            time.sleep(delay)
            self.setStep(1, 0, 0, 1)
            time.sleep(delay)
            i += 1

    def backwards(self, steps):
        i = 0
        delay = self.delay
        while i in range(0, steps):
            self.setStep(1, 0, 0, 1)
            time.sleep(delay)
            self.setStep(0, 1, 0, 1)
            time.sleep(delay)
            self.setStep(0, 1, 1, 0)
            time.sleep(delay)
            self.setStep(1, 0, 1, 0)
            time.sleep(delay)
            i += 1

    def setStep(self, w1, w2, w3, w4):
        self.coil_A_1_pin.value = w1
        self.coil_A_2_pin.value = w2
        self.coil_B_1_pin.value = w3
        self.coil_B_2_pin.value = w4

while True:
    user_delay = input("Delay between steps (milliseconds)?")
    user_steps = input("How many steps forward? ")
    stepper = Stepper()
    stepper.delay = int(user_delay)
    stepper.forward(int(user_steps))
    user_steps = input("How many steps backwards? ")
    stepper.backwards(int(user_steps))
