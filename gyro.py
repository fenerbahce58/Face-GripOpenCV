#!/usr/bin/python
import smbus
import math
import matplotlib.pyplot as plt
from time import sleep, strftime, time
 
# Register
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
 
def read_byte(reg):
    return bus.read_byte_data(address, reg)
 
def read_word(reg):
    h = bus.read_byte_data(address, reg)
    l = bus.read_byte_data(address, reg+1)
    value = (h << 8) + l
    return value
 
def read_word_2c(reg):
    val = read_word(reg)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):
    return math.sqrt((a*a)+(b*b))
 
def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)
 
def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

bus = smbus.SMBus(1) # bus = smbus.SMBus(0) fuer Revision 1
address = 0x68       # via i2cdetect
 
# Aktivieren, um das Modul ansprechen zu koennen
bus.write_byte_data(address, power_mgmt_1, 0)
 
print()
print("accelerationsensor")
print("---------------------")
 
def runner():
    looper=0
    with open("/home/pi/metin/mpuLog{0}.csv".format(time()), "a") as log:
        log.write("x,y,z,time\n")
        while(True):
            acceleration_xout = read_word_2c(0x3b)
            acceleration_yout = read_word_2c(0x3d)
            acceleration_zout = read_word_2c(0x3f)
            
            acceleration_xout_scaled = acceleration_xout / 16384.0
            acceleration_yout_scaled = acceleration_yout / 16384.0
            acceleration_zout_scaled = acceleration_zout / 16384.0
            
            test = log.write("{0},{1},{2},{3}\n".format(str(acceleration_xout),str(acceleration_yout),str(acceleration_zout),strftime("%Y-%m-%d %H:%M:%S")))
            looper+=1
            print(looper)
            sleep(1)


runner()
