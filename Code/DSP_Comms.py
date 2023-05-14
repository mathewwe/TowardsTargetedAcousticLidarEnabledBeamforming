import numpy as np
import spidev

bus = 0
device = 0
spi = spidev.SpiDev()

spi.open(bus,device)
spi.max_speed_hz = 500000
spi.mode = 0

val = np.double(0.3563)
# val = np.double(0)
val = np.double(0.2207)

addr_list = [21, 23, 25, 27, 29, 31, 33, 35]

def float_to_fixedpoint(value):
    return np.int32(value * (0x01 << 24))

def fixedpoint_to_bytes(fixpt_val):
    bytes_list = []
    bytes_list.append(int((np.int32(fixpt_val) >> 24) & 0xFF))
    bytes_list.append(int((np.int32(fixpt_val) >> 16) & 0xFF))
    bytes_list.append(int((np.int32(fixpt_val) >> 8) & 0xFF))
    bytes_list.append(int((np.int32(fixpt_val))&0xFF))
    return bytes_list

write_data_header = [0x00, 0x60, 0x00]
write_addr_header = [0x00, 0x60, 0x05]
read_header = [0x01, 0x00, 0x1F]
# msg consists of [r/w, addr_upper, addr_lower, data, data, ...]
fixedpoint = float_to_fixedpoint(val)
byte_list = fixedpoint_to_bytes(fixedpoint)

print(val)
print(fixedpoint)

data_msg = write_data_header + byte_list 
print("Write Data Msg:")
for byte in data_msg:
    print(hex(byte))
spi.xfer2(data_msg)

addr_to_write = [0x00, 0x00, 0x00, 0x1F]
words_to_write = [0x00, 0x00, 0x00, 0x01]
extra_stuff = [0x00, 0x00, 0x00, 0x00]
addr_msg = write_addr_header + addr_to_write + words_to_write + extra_stuff
print("Wrote delay")
spi.xfer2(addr_msg)
