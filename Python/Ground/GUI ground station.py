import sys
sys.path.append('..')

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Radio:
    
    def __init__():
        pass
    
    def recv(self):
        pass

    def send(self ):
        pass


class Packet:
    def __init__(self, timestamp='', temperature='', pressure='', humidity='', gps_position='', acceleration='', magnetometer_reading='', altitude=''):
        self.timestamp = timestamp
        self.temperature = temperature
        self.pressure = pressure
        self.humidity = humidity
        self.gps_position = gps_position
        self.acceleration = acceleration
        self.magnetometer_reading = magnetometer_reading
        self.altitude = altitude
        
    def encode(self):
        # Encode the packet into a string
        packet_string = ';'+ str(self.timestamp) + ";" + str(self.temperature) + ";" + str(self.pressure) + ";"
        packet_string += str(self.humidity) + ";" + str(self.gps_position) + ";" + str(self.acceleration) + ";"
        packet_string += str(self.magnetometer_reading) + ';' + str(self.altitude) + ';'
        return packet_string
    
    def decode(self, bytestream):
        # Decode the bytestream and update the packet's attributes
        if bytestream == None:
            SD_o.write("No data to decode")
            return
        packet_string = str(bytestream).strip()
        packet_parts = packet_string.split(";")[1:-1]
        print(packet_parts)


        # assigning values from packet
        if packet_parts[0] != '':
            self.timestamp = packet_parts[0]
        if packet_parts[1] != '':
            self.temperature = float(packet_parts[1])
        if packet_parts[2] != '':
            self.pressure = float(packet_parts[2])
        if packet_parts[3] != '':
            self.humidity = float(packet_parts[3])
        if packet_parts[4] != '':
            self.gps_position = l_eval(packet_parts[4])
        if packet_parts[5] != '':
            self.acceleration = l_eval(packet_parts[5])
        if packet_parts[6] != '':
            self.magnetometer_reading = l_eval(packet_parts[6])
        if packet_parts[7] != '':
            self.altitude = float(packet_parts[7])

    def __str__(self) -> str:
        return f"Packet({self.timestamp},{self.temperature},{self.pressure},{self.humidity},\
            {self.gps_position},{self.acceleration},{self.magnetometer_reading},{self.altitude})"

    
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class RadioAppWindow(Gtk.Window):

    radio = Radio()

    def __init__(self):
        Gtk.Window.__init__(self, title="Radio App")

        builder = Gtk.Builder()
        builder.add_from_file("radio_app.glade")
        self.window = builder.get_object("window1")
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

        self.add(self.window)
        self.listener_thread = threading.Thread(target=self.listen_for_radio)
        self.listener_thread.start()
        self.send_button.connect("clicked", self.send_GPS_Pos)


    def listen_for_radio(self):
        while True:
            self.radio.recv()
            def update():
                # Update the liststore with the data from the packet
                self.liststore.append([packet.timestamp, str(packet.temperature), str(packet.pressure), str(packet.humidity), str(packet.gps_position), str(packet.acceleration), str(packet.magnetometer_reading), str(packet.altitude)])

                # If there are more than 10 packets in the liststore, remove the oldest one
                if len(self.liststore) > 10:
                    self.liststore.remove(self.liststore[0].iter)

            # Schedule the update function to be called in the main GTK thread
            GObject.idle_add(update)


    def send_GPS_Pos(self, widget):
        # Get the text from the text input widget
        gps_pos_text = self.GPSPos_in.get_text()

        # Try to parse the text as a tuple of two floats
        try:
            gps_pos = tuple(float(x) for x in gps_pos_text.split(','))
        except ValueError:
            # If the text could not be parsed as a tuple of floats, show an error message and return
            self.error_dialog.show()
            return

        # Create a new Packet object with the parsed GPS position
        packet = Packet(gps_position=gps_pos)

        # Send the encoded packet over the radio
        self.radio.send(packet.encode())
   

win = RadioAppWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
