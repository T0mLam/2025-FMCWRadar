import csv
import serial
import argparse
from enum import Enum
from parseFrame import *

# For Timer
import threading
import sys

## Main user parameters
parser = argparse.ArgumentParser(prog='L6432_Parsing',
                                 description="mmWave TLV parser", usage='%(prog)s [options]',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 add_help=True)
parser.add_argument("-p", "--port", type=str, help="comms port")
parser.add_argument("-c", "--config", type=str, help="config file")
args = parser.parse_args()
if len(sys.argv) < 2:
    parser.print_help()
    exit()
cmdline = vars(args)

# COMport for EVM connection.
UARTUserComPort = cmdline['port']
# Config file sent on startup.
ConfigFileName = cmdline['config']

DEBUG = 0                                               # Debug flags for extra console prints.
CSV = 1                                                 # Enable CSV recording of data
FRAME_COUNT = 10000                                       # How many frames to collect
HEADERLENGTH = 40                                       # TLV Header length in Bytes (fixed)
frameCount = 0                                          # counting frames for inserting into CSV
OldFrameNumber = 0                                      # checking for out of sequence frames.
ErrorCount = 0                                          # error count from out of sequence frames.
UARTUserComSpeed = 115200  #1250000                     # startup serial baud rate
UART = 0

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
        # UART = serial.Serial(UARTUserComPort, 1250000)           #x432
        # DATA = serial.Serial('COM4', 921600, timeout=0)
    except Exception as e:
        print(e)

def reconnect_ports(NewBaudRate):
    global UART
    try:
        UART.close()
        UART = serial.Serial(UARTUserComPort, NewBaudRate)
        UART.write(('\n').encode())
        t = UART.read_all().decode()

    except Exception as e:
        print(e)

# Send config file to target. 
def send_cfg():
    print(f"Config file: sending {ConfigFileName}")
    try:
        config = [line.rstrip('\r\n') for line in open(ConfigFileName)]
        for i in config:
            if "%" in i:
                continue
            UART.write((i + '\n').encode())

            if "baudRate 1250000" in i:
                reconnect_ports(1250000)
                if DEBUG: print(i)
            if "baudRate 115200" in i:
                reconnect_ports(115200)
                if DEBUG: print(i)
            time.sleep(0.05)
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


# Parse the UART stream.
def parse():
    global OldFrameNumber, ErrorCount
    global frameCount

    # Look for sync word and read in header, and then totalpacket for 1st iteration.
    outputPacket = read_all()
    offset = outputPacket.find(UART_MAGIC_WORD)
    while offset == -1:
        outputPacket += read(len(UART_MAGIC_WORD))
        offset = outputPacket.find(UART_MAGIC_WORD)
    outputPacket = outputPacket[offset:]

    outputPacket += read(HEADERLENGTH - len(UART_MAGIC_WORD))
    magic, version, totalPacketLen, platform, frameNum, timeCPUCycles, numDetectedObj, numTLVs, subFrameNum = \
        struct.unpack('Q8I', outputPacket[:HEADERLENGTH])
    outputPacket += read(totalPacketLen - HEADERLENGTH)

    if CSV:
        # define the time-stamped CSV file name
        t = time.localtime()
        current_time = time.strftime("%H%M%S", t)

        # Open and initialise the tracker CSV file, write the column headers
        # CSV_FILE_t = 'results_tracker_' + current_time + '.csv'
        # csvfile_t = open(CSV_FILE_t, "w", newline='')
        # fieldnames_t = ['Frame count', 'Track ID', 'posy', 'posz', 'vely', 'velz', 'accy', 'accz']
        # writer_t = csv.DictWriter(csvfile_t, fieldnames=fieldnames_t)
        # writer_t.writeheader()

        # Open and initialise the point cloud CSV file, write the column headers
        CSV_FILE = 'results_' + current_time + '.csv'
        csvfile = open(CSV_FILE, "w", newline='')
        fieldnames = ['Frame count', 'Track ID', 'posy', 'posz', 'vely', 'velz', 'accy', 'accz']
        for i in range(50):                     # create headers for a variable number of points.
            fieldnames.append('pointy%d' % i)
            fieldnames.append('pointz%d' % i)
            fieldnames.append('snr%d' % i)
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)

        print(f"CSVfile: writing to {CSV_FILE}")

    ## Loop through the UART frame data from the radar board
    while frameCount < FRAME_COUNT:
        frameCount += 1

        # read frame header and TLVs for dict storage
        frameDict = parseStandardFrame(outputPacket, DEBUG)

        # Check if targets have been detected for logging into CSV.
        # TLV = 308, MMWDEMO_OUTPUT_EXT_MSG_TARGET_LIST
        if 'numDetectedPoints' in frameDict and 'target_list' in frameDict:
            row = []
            if 'target_list' in frameDict:
                numDetectedTargets, targets = parseTrackTLV(frameDict['target_list'], frameDict['tlvLength'])
                for i in range(numDetectedTargets):
                    print("Target Median Range:\t%.2f" % targets[i, 2])
                    print("Target Median Height:\t%.2f\n" % targets[i, 1])
                    row.append(frameDict['frameNum'])   # frame number
                    row.append(int(targets[i, 0]))      # trackID
                    row.append(round(targets[i, 2], 2)) # posy
                    row.append(round(targets[i, 1], 2)) # posz
                    row.append(round(targets[i, 5], 2)) # vely
                    row.append(round(targets[i, 4], 2)) # velz
                    row.append(round(targets[i, 8], 2)) # accy
                    row.append(round(targets[i, 7], 2)) # accz

                # Check if point cloud have been detected for logging into CSV.
                # TLV = 301, MMWDEMO_OUTPUT_EXT_MSG_DETECTED_POINTS
                if 'pointCloud' in frameDict:
                    ## Extract the range, height (90deg rotated board) and SNR of the objects detected
                    for i in range(frameDict['numDetectedPoints']):
                        row.append(round(frameDict['pointCloud'][i][1],2))  #y
                        row.append(round(frameDict['pointCloud'][i][0],2))  #z
                        row.append(round(frameDict['pointCloud'][i][4],2))  #SNR
                        
                    # populate the CSV file.
                    writer.writerow(row)

        # check for jumps in the framenumber
        if frameNum - OldFrameNumber != 1:
            ErrorCount = ErrorCount + 1
            if DEBUG: print("ErrorCount:\t%i " % ErrorCount)
        OldFrameNumber = frameNum

        # resize data buffer
        outputPacket = outputPacket[totalPacketLen:]
        outputPacket += read(len(UART_MAGIC_WORD) - len(outputPacket))

        # start to look for the next packet
        offset = outputPacket.find(UART_MAGIC_WORD)
        while offset == -1:
            outputPacket += read(len(UART_MAGIC_WORD))
            offset = outputPacket.find(UART_MAGIC_WORD)
        outputPacket = outputPacket[offset:]
        outputPacket += read(HEADERLENGTH - len(UART_MAGIC_WORD))

        # Read in the next frame of data
        magic, version, totalPacketLen, platform, frameNum, timeCPUCycles, numDetectedObj, numTLVs, subFrameNum = struct.unpack(
            'Q8I', outputPacket[:HEADERLENGTH])
        outputPacket += read(totalPacketLen - HEADERLENGTH)

    if CSV:
        csvfile.close()
        os.system(osString)
        print(f"\nCSVFile: closed and moved")


def timer_kill(duration):
    print(f"Timer started. Program will terminate in {duration // 60} minutes.")
    timerThread = threading.Timer(duration, lambda: sys.exit(0))
    timerThread.daemon = True
    timerThread.start()


## Main
TIMER_DURATION = 600
connect_ports()
timer_kill(TIMER_DURATION)
while 1:
    try:
        if ConfigFileName != None:
            send_cfg()
        parse()
        UART.close()
        exit()
    except serial.SerialTimeoutException:
        print('Data could not be read')
        time.sleep(1)
