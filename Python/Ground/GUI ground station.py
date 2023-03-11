#!/bin/python3

import sys
from collections import deque
sys.path.append('..')
packet_queue = deque()

from Can.new_Packet import Packet, PacketType, Command
import Can.comms as comms
import gi
import time
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib
import threading, traceback
from ast import literal_eval as l_eval

max_not_none_timestamp = time.time()
first_timestamp = time.time() 
comms.SD_o = comms.SD('log.txt')


class RadioAppWindow:

    radio = comms.Radio()

    def __init__(self):
        #Gtk.Window.__init__(self, title="Radio App")

        builder = Gtk.Builder()
        builder.add_from_file("GUI_ground_station.glade")
        self.window = builder.get_object("window1")
        
        self.window.show()
        self.scrolled_window = builder.get_object("scrolledwindow1")
        self.treeview = builder.get_object("treeview1")
        self.send_button = builder.get_object("send_button")

        # Set up the treeview to display the data from the packets
        self.liststore = Gtk.ListStore(str, str, str, str, str, str, str, str)
        self.treeview.set_model(self.liststore)
        for i, column_title in enumerate(["Timestamp", "Temperature", "Pressure", "Humidity", "GPS Position", "Acceleration", "Magnetometer Reading", "Altitude"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)

        self.GPSPos_in = builder.get_object('GPSPos_in')
        self.pressure_in = builder.get_object('pressure_in')
        #self.add(self.window)
        self.listener_thread = threading.Thread(target=self.listen_for_radio)
        self.listener_thread.start()
        # self.send_button.connect("clicked", self.send_GPS_Pos)
        self.GPSPos_in.connect('activate', self.send_GPS_Pos)
        self.pressure_in.connect('activate', self.send_Press)


    def update(self):
        while len(packet_queue):
            packet = packet_queue.popleft()
            comms.SD_o.write(str(packet) + 'packet in GUI update')
            # Update the liststore with the data from the packet
            self.liststore.append([packet.timestamp, str(packet.temperature), str(packet.pressure), str(packet.humidity), str(packet.gps_position), str(packet.acceleration), str(packet.magnetometer_reading), str(packet.altitude)])

            # If there are more than 10 packets in the liststore, remove the oldest one
            if len(self.liststore) > 10:
                self.liststore.remove(self.liststore[0].iter)


    def listen_for_radio(self):
        while True:
            packet = Packet(timestamp=time.ctime(), temperature=None)
            packet.decode(self.radio.recv())
            if not (packet.temperature is None):
                max_not_none_timestamp = time.time()
                comms.SD_o.write(f'{max_not_none_timestamp - first_timestamp} time difference')
                comms.SD_o.write(str(packet) + 'packet')
                comms.SD_o.write(str(packet.temperature) + 'tempval')
                packet_queue.append(packet)

            # Schedule the update function to be called in the main GTK thread
            GLib.idle_add(self.update)


    def send_GPS_Pos(self, widget):
        # Get the text from the text input widget
        gps_pos_text = self.GPSPos_in.get_text()

        # Try to parse the text as a tuple of two floats
        try:
            gps_pos = tuple(float(x) for x in gps_pos_text.split(','))
        except ValueError:
            # If the text could not be parsed as a tuple of floats, show an error message and return
            comms.SD_o.write(traceback.format_exc())
            gps_pos = None
        
        

        # Create a new Packet object with the parsed GPS position
        packet = Packet.create_command_packet(time.time(), Command.SLEEP, *gps_pos)

        # Send the encoded packet over the radio
        self.radio.send(packet.encode())
        print('sent')
        
    def sendPress(self, widget):
        
        pressure_text = self.pressure_in.get_text()       
        try: 
            press = float(pressure_text)
            packet = Packet.create_command_packet(time.time(), Command.SLEEP, press)
            self.radio.send(packet.encode())
        except ValueError:
            comms.SD_o.write(traceback.format_exc())
   


app = RadioAppWindow()
win = app.window
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

