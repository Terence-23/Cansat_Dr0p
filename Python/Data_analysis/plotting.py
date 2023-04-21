import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from bisect import bisect_left
import sys

def v_length(x, y, z = None) -> float:
    if z is None:
        return np.sqrt(x*x + y*y)
    return np.sqrt(x*x + y*y + z*z)


def read_data(path = 'Data/'):
    
    with open(path + 'extended_c.csv') as f:
        ext_csv = [[float(v) for j, v in enumerate(i.strip().split(',')) if j != 12] for i in f.readlines()[621:1400]]
    
    with open(path + 'base_c.csv') as f:
        b_csv = [[float(j) for j in i.strip().split(',')[:-1]] for i in f.readlines()[3139:4579]]

#    read lats and lons
    timestamps = [i[0] for i in ext_csv]
    lats = [i[1] for i in ext_csv]
    lons = [i[2] for i in ext_csv]
    
    with open(path + 'extended_c.csv') as f:
        accs = [v_length(*[j for j in map(float, i.strip().split(',')[3:6])]) for i in f.readlines()[521:1400]]
    
    headings = [i[9] for i in ext_csv]
    des_headings = [i[10] for i in ext_csv]
    
    h_speeds = [i[11] for i in ext_csv]
    
    alts = []
    temps = []
    press = []
    hums = []
    v_speed = []
    for i in timestamps:
        ind = bisect_left([j[0] for j in b_csv], i)
        alts.append(b_csv[ind][4])
        temps.append(b_csv[ind][1])
        press.append(b_csv[ind][2])
        hums.append(b_csv[ind][3])
        v_speed.append(b_csv[ind][5])
        
    
    return timestamps, lats, lons, accs, h_speeds,  headings, des_headings, temps, press, hums, alts, v_speed



timestamps, lats, lons, accs, h_speeds,  headings, des_headings, temps, press, hums, alts, v_speed = read_data()

packet_num = np.linspace(0, len(lats), len(lats))

# Headings

fig, ax = plt.subplots(figsize=(16, 9), layout='constrained')

ax.plot(packet_num, headings, label='heading')  # Plot some data on the axes.
ax.plot(packet_num, des_headings, label='optimal heading')  # Plot more data on the axes...
ax.set_xlabel('number of packet')  # Add an x-label to the axes.
ax.set_ylabel('deg')  
ax.set_title("Heading vs. desired heading")  # Add a title to the axes.

fig.legend(loc='upper right')
fig.savefig('Renders/You spin me round.png', dpi = 400)

# Press and Alt

fig, ax = plt.subplots(figsize=(16, 9), layout='constrained')

ax.plot(packet_num, press, label='Pressure')  # Plot some data on the axes.
ax.set_xlabel('number of packet')  # Add an x-label to the axes.
ax.set_ylabel('hPa')  

ax2 = ax.twinx()
ax2.plot(packet_num, alts, label='Altitude', color='red')
ax2.set_ylabel('m')# Plot more data on the axes...

ax.set_title("Pressure & altitude")  # Add a title to the axes.

fig.legend(loc='upper right')
fig.savefig('Renders/Presssure & altitude.png', dpi = 400)


# Temp and Hum

fig, ax = plt.subplots(figsize=(16, 9), layout='constrained')

ax.plot(packet_num, temps, label='Temperature')  # Plot some data on the axes.
ax.set_xlabel('number of packet')  # Add an x-label to the axes.
ax.set_ylabel('°C')  

ax2 = ax.twinx()
ax2.plot(packet_num, hums, label='Relative humidity', color='red')
ax2.set_ylabel('%')# Plot more data on the axes...

ax.set_title("Temperature & humidity")  # Add a title to the axes.

fig.legend(loc='upper right')
fig.savefig('Renders/Temperature & humidity.png', dpi = 400)

# speeds

fig, ax = plt.subplots(figsize=(16, 9), layout='constrained')

ax.plot(packet_num, h_speeds, label='Horizontal speed')  # Plot some data on the axes.
ax.set_xlabel('number of packet')  # Add an x-label to the axes.
ax.set_ylabel('m/s')  
ax.plot(packet_num, v_speed, label='Vertical speed')

ax.set_title("Speed")  # Add a title to the axes.
    
fig.legend(loc='upper right')
fig.savefig('Renders/I am speed.png', dpi = 400)

# acceleration

packet_num = np.linspace(-100, len(lats), len(accs))
fig, ax = plt.subplots(figsize=(16, 9), layout='constrained')

ax.plot(packet_num, accs, label='Acceleration')  # Plot some data on the axes.
ax.set_xlabel('number of packet')  # Add an x-label to the axes.
ax.set_ylabel('m/s²')

ax.set_title("Acceleration")  # Add a title to the axes.
    
fig.legend(loc='upper right')
fig.savefig('Renders/Gravity.png', dpi = 400)
    
plt.show()
    