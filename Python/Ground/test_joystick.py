#!/usr/bin/env python

from pyPS4Controller.controller import Controller
from pyPS4Controller.event_mapping.DefaultMapping import DefaultMapping
import sys
import multiprocessing


class MyController(Controller):

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)

    def on_x_press(self):
       print("Hello world")

    def on_x_release(self):
       print("Goodbye world")


controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
# you can start listening before controller is paired, as long as you pair it within the timeout window
multiprocessing.Process( target=controller.listen).start()

print("end")
sys.exit()

