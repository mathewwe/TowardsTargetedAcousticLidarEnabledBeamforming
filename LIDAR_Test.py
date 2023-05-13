from rplidar import RPLidar
from time import sleep
import signal
import sys
import numpy as np

lidar = RPLidar('/dev/ttyUSB0')

def signal_handler(sig, frame):
        lidar.stop()
        lidar.stop_motor()
        lidar.disconnect()
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
#info = lidar.get_info()
#print(info)

health = lidar.get_health()
print(health)

for scan in lidar.iter_scans():
        sorted_scan = sorted(scan, key=lambda x: x[-1])
        sorted_scan = [element for element in sorted_scan if element[1] > 180]
        print(sorted_scan)
lidar.stop()
lidar.stop_motor()
lidar.disconnect()
