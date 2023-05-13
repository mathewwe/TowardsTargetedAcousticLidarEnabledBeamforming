import numpy as np
import spidev
import time
import signal
import sys

# Functions
def signal_handler(sig, frame):
    print("")
    print('Quitting...')
    sys.exit(0)

def float_to_fixedpoint(value):
    return np.int32(value * (0x01 << 24))

def fixedpoint_to_bytes(fixpt_val):
    bytes_list = []
    bytes_list.append(int((np.int32(fixpt_val) >> 24) & 0xFF))
    bytes_list.append(int((np.int32(fixpt_val) >> 16) & 0xFF))
    bytes_list.append(int((np.int32(fixpt_val) >> 8) & 0xFF))
    bytes_list.append(int((np.int32(fixpt_val))&0xFF))
    return bytes_list

# SPI/Comms Parameters
bus = 0
device = 0
spi = spidev.SpiDev()

spi.open(bus,device)
spi.max_speed_hz = 500000
spi.mode = 0

# Constants

fs = 48000
v_s = 343
w = 0.04
a = 0.04
num_speakers = 8

# SIGINT Handler
signal.signal(signal.SIGINT, signal_handler)

addr_list = [21, 29, 23, 31, 25, 33, 27, 35]
print("Addresses of parameters to change: [", end=" ")
for addr in addr_list:
    print(hex(addr), end=" ")
print("]")
print("")

# Phased Array Parameters
while True:
    theta = float(input("Angle in degrees of desired beam direction:\n"))
    dist = float(input("Distance of listener in meters from center of array:\n"))
    
    reverse = 0
    if(theta>90):
        theta = 180 - theta
        reverse = 1
    theta = np.deg2rad(theta)
    # msg consists of [r/w, addr_upper, addr_lower, data, data, ...]
    write_data_header = [0x00, 0x60, 0x00]
    write_addr_header = [0x00, 0x60, 0x05]
    read_header = [0x01, 0x00, 0x1F]
    words_to_write = [0x00, 0x00, 0x00, 0x01]
    extra_stuff = [0x00, 0x00, 0x00, 0x00]

    # Data Storage Structures
    theta_arr = np.zeros((num_speakers,1))
    dist_arr = np.zeros((num_speakers,1))
    delay_arr = np.zeros((num_speakers,1))

    b = abs(dist*np.cos(theta))
    h = dist*np.sin(theta)

    for i in range(1,num_speakers+1):
        theta_arr[i-1] = np.arctan(h/(max(b, (3.5-(i-1))*(w+a)) - min(b, (3.5-(i-1)) *(w+a))))
        dist_arr[i-1] = h*np.sin(theta)/(np.sin(theta_arr[i-1]))
        
    if reverse: 
        theta_arr = np.flipud(theta_arr).flatten()
        dist_arr = np.flipud(dist_arr).flatten()
        
    ref = max(dist_arr)
    delay_time = 1

    for i in range(1,num_speakers+1):
        delay_time = (ref - dist_arr[i-1]) / v_s
        delay_arr[i-1] = delay_time * fs
        
    delay_arr = tuple(delay_arr)

    for n, delay in enumerate(delay_arr):
        delay_to_write = delay/100

        fixedpoint = float_to_fixedpoint(delay_to_write)
        byte_list = fixedpoint_to_bytes(fixedpoint)
        data_msg = write_data_header + byte_list
        print("Data Message: [", end=" ")
        for byte in data_msg:
            print(hex(byte), end=" ")
        print("]")
        spi.writebytes(data_msg)
        time.sleep(0.001)

        addr_to_write = [0x00, 0x00, 0x00, addr_list[n]]
        addr_msg = write_addr_header + addr_to_write + words_to_write + extra_stuff
        spi.writebytes(addr_msg)
        print("Wrote delay of " + str(delay) + " samples to speaker " + str(n+1))
        time.sleep(0.02)
        print("")
    print("")