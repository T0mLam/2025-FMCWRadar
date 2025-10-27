import serial
import time
import logging
import struct
from enum import Enum
import math
from parseFrame import *
import csv
import shutil

# This program just sends CFG and dumps the result - no parsing included - and can therefore operate as a single file.

# Main user parameters
UARTUserComPort = 'COM7'  # COMport for EVM connection.
FRAME_COUNT = 100  # How many frames to collect
ConfigFileName = 'configs\gesture_recognition_2m_xwrl6432.cfg'  # Config file sent on startup.
# ConfigFileName = 'PresenceDetect.cfg'

DEBUG = 1  # Debug flags for extra console prints.
HEADERLENGTH = 40  # TLV Header length in Bytes (fixed)
frameCount = 0  # counting frames for inserting into CSV
OldFrameNumber = 0  # checking for out of sequence frames.
ErrorCount = 0  # error count from out of sequence frames.
UARTUserComSpeed = 115200  # startup serial baud rate

class PointC(Enum):
    x, y, z, v, SNR = [0, 1, 2, 3, 4]

# Converts data to bytes
class convert(bytes):
    def __str__(self):
        return 'b\'{}\''.format(''.join('\\x{:02x}'.format(b) for b in self))


def connect_ports():
    global UART
    # global DATA
    try:
        UART = serial.Serial(UARTUserComPort, UARTUserComSpeed)  # x432
    except Exception as e:
        print(e)


def reconnect_ports(NewBaudRate):
    global UART
    try:
        UART.close()
        UART = serial.Serial(UARTUserComPort, NewBaudRate)
    except Exception as e:
        print(e)

# Send config file to target.
def send_cfg():
    print(f"Config file: sending {ConfigFileName}")
    try:
        config = [line.rstrip('\r\n') for line in open(ConfigFileName)]
        for i in config:
            UART.write((i + '\n').encode())
            time.sleep(0.05)
            if "baudRate 115200" in i:
                reconnect_ports(115200)
                if DEBUG: print(i)
            if "baudRate 1250000" in i:
                reconnect_ports(115200)
                if DEBUG: print(i)
            t = UART.read_all().decode()
            if DEBUG: print(t)

        # mmWResponse = UART.read_all()
        mmWResponse = read_all()
        while mmWResponse != b'Done\r\n':
            mmWResponse += read(1)
        if DEBUG: print(mmWResponse.decode())

    except NameError:
        print(f"Config file: file not found")

    print(f"Config file: sent")


# read serial port: Read all bytes currently available in the buffer of the OS
def read_all():
    output = UART.read_all()
    return convert(output)


# read serial port: Read all bytes currently available in the buffer of the OS
def read(length):
    output = UART.read(length)
    return convert(output)

# Dump the UART stream.
def dump():
    print(f"\nDumping RX data")
    while 1:
        outputPacket = read_all()
        if outputPacket != b'':
            print(outputPacket)

## Main
connect_ports()
while 1:
    try:
        send_cfg()
        dump()
        UART.close()
        exit()
    except serial.SerialTimeoutException:
        print('Data could not be read')
        time.sleep(1)
