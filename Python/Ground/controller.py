#!/usr/bin/env python

from pyPS4Controller.controller import Controller
from multiprocessing import Value


class MyController(Controller):
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        self.joystick_vert = Value("d", 0)
        self.joystick_hor = Value("d", 0)
        self.isR2Pressed = Value("i", 0)

    def on_L3_left(self, value):
        self.joystick_hor.value = value / 32767

    def on_L3_right(self, value):
        self.joystick_hor.value = value / 32767

    def on_L3_up(self, value):
        self.joystick_vert.value = value / 32767

    def on_L3_down(self, value):
        self.joystick_vert.value = value / 32767

    def on_R2_press(self, val):
        self.isR2Pressed.value = 1
        print(f"Entering manual mode, val: {val}")

    def on_R2_release(self):
        self.isR2Pressed.value = 0
        print("Exiting manual mode")


controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
# you can start listening before controller is paired, as long as you pair it within the timeout window
controller.listen(timeout=60)
