#!/bin/python3
import comms, sensor
import time

def main():
    comms.SD_o = comms.SD('log.out')
    comms.Packet.decode("w11;a10;o11;p;h")


if __name__ =="__main__":
    main()