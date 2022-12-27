#!/bin/bash
# install all pip libs

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

echo "Install pip libraries.
Make sure that pip3 is installed"

pip3 install --upgrade setuptools adafruit-python-shell adafruit-circuitpython-rfm9x adafruit-circuitpython-bme680 adafruit-circuitpython-lsm303-accel adafruit-circuitpython-lis2mdl
