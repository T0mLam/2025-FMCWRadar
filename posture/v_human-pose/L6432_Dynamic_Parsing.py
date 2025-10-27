import csv
import serial
import argparse
from enum import Enum
from parseFrame import *

import threading
import sys

import msvcrt

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
VELOCITY_THRESHOLD = -0.25                             # Downward velocity threshold (negative indicates downward motion)
  
RECORDING = False                                       # Flag for recording data
WAITING_FOR_MOVEMENT = True                             # Flag for waiting for start of recording
SHOULD_EXIT = False
ACTION_TYPE = None                                      # Type of action being recorded ('sitting' or 'falling')

current_csvfile = None                                  # Current CSV file handle
current_writer = None                                   # Current CSV writer object
sitting_csvfile, falling_csvfile = None, None
sitting_writer, falling_writer = None, None
recording_counter = 0
action_sequence = 0
session_id = 0


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
    global OldFrameNumber, ErrorCount, frameCount
    global WAITING_FOR_MOVEMENT, RECORDING, SHOULD_EXIT
    global action_sequence, session_id, recording_counter

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

    ## Loop through the UART frame data from the radar board
    # while frameCount < FRAME_COUNT:
    while not SHOULD_EXIT:
        frameCount += 1

        # read frame header and TLVs for dict storage
        frameDict = parseStandardFrame(outputPacket, DEBUG)

        # Check if targets have been detected for logging into CSV.
        # TLV = 308, MMWDEMO_OUTPUT_EXT_MSG_TARGET_LIST
        if 'numDetectedPoints' in frameDict and 'target_list' in frameDict:
            if 'target_list' in frameDict:
                numDetectedTargets, targets = parseTrackTLV(frameDict['target_list'], frameDict['tlvLength'])
                for i in range(numDetectedTargets):
                    # Get z velocity for movement detection
                    velz = round(targets[i, 4], 2)

                    # print("Target Median Range:\t%.2f" % targets[i, 2])
                    # print("Target Median Height:\t%.2f\n" % targets[i, 1])
                    # print("Target Z velocity:\t%.2f\n" % velz)

                    # Detect start of downward movement
                    if not WAITING_FOR_MOVEMENT and velz < VELOCITY_THRESHOLD:
                        RECORDING = True
                        print(f"Movement detected! Recording {ACTION_TYPE} motion...")
                    
                    # Detect end of movement (when velocity is close to zero)
                    # if RECORDING and abs(velz) < abs(VELOCITY_THRESHOLD/2):
                    if RECORDING and velz > VELOCITY_THRESHOLD:
                        RECORDING = False
                        WAITING_FOR_MOVEMENT = True
                        print(f"Motion complete! Press 1 for sitting or 2 for falling to record another motion.")

                    # Only build and record data row if we're in recording state
                    if RECORDING and current_writer:
                        action_sequence += 1
                        base_row = [
                            frameDict['frameNum'],   # frame number
                            int(targets[i, 0]),      # trackID
                            round(targets[i, 2], 2), # posy
                            round(targets[i, 1], 2), # posz
                            round(targets[i, 5], 2), # vely
                            velz,                    # velz
                            round(targets[i, 8], 2), # accy
                            round(targets[i, 7], 2), # accz
                        ]

                        point_data = []
                        # Add point cloud data if available
                        if 'pointCloud' in frameDict:
                            for j in range(frameDict['numDetectedPoints']):
                                point_data.append(round(frameDict['pointCloud'][j][1],2))  # y
                                point_data.append(round(frameDict['pointCloud'][j][0],2))  # z
                                point_data.append(round(frameDict['pointCloud'][j][4],2))  # SNR
                            
                            # # Write the data only while recording
                            # current_writer.writerow(row)
                        
                        full_row = [
                            session_id,
                            recording_counter,
                            action_sequence,
                        ]  + base_row + point_data

                        current_writer.writerow(full_row)

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

        if SHOULD_EXIT:
            break

def initialize_csv_files():
    global sitting_csvfile, falling_csvfile, sitting_writer, falling_writer
    
    t = time.localtime()
    timestamp = time.strftime("%H%M%S", t)
    
    sitting_filename = f'results_sitting_{timestamp}.csv'
    falling_filename = f'results_falling_{timestamp}.csv'
    
    sitting_csvfile = open(sitting_filename, "w", newline='')
    falling_csvfile = open(falling_filename, "w", newline='')
    
    # create headers for a variable number of points.
    fieldnames = [
        'Session_ID',         
        'Recording_Number',   
        'Sequence_Number',           
        'Frame_count', 
        'Track_ID', 
        'posy', 'posz', 'vely', 'velz', 'accy', 'accz'
    ]
    
    for i in range(50):
        fieldnames.append(f'pointy{i}')
        fieldnames.append(f'pointz{i}')
        fieldnames.append(f'snr{i}')
    
    sitting_writer = csv.writer(sitting_csvfile)
    falling_writer = csv.writer(falling_csvfile)
    
    sitting_writer.writerow(fieldnames)
    falling_writer.writerow(fieldnames)
    
    print(f"CSV files initialized:")
    print(f"  Sitting data: {sitting_filename}")
    print(f"  Falling data: {falling_filename}")

def setup_new_recording(action_type):
    global ACTION_TYPE, current_writer, session_id, recording_counter, action_sequence
    
    t = time.localtime()
    session_id = int(time.strftime("%H%M%S", t))
    recording_counter += 1
    action_sequence = 0
    
    if action_type == 'sitting':
        current_writer = sitting_writer
    elif action_type == 'falling':
        current_writer = falling_writer
    else:
        print(f"Unknown action type: {action_type}")
        return
    
    ACTION_TYPE = action_type
    print(f"Ready to record {action_type} motion #{recording_counter} (Session ID: {session_id})")

def keyboard_listener():
    global WAITING_FOR_MOVEMENT, RECORDING, ACTION_TYPE, SHOULD_EXIT
    
    print("\nKeyboard listener started.")
    print("Press 1 for sitting recording")
    print("Press 2 for falling recording")
    print("Press q to quit")
    
    while not SHOULD_EXIT:
        if msvcrt.kbhit():  
            key = msvcrt.getch().decode().lower()
            if not RECORDING and WAITING_FOR_MOVEMENT:
                if key == '1':
                    setup_new_recording('sitting')
                    WAITING_FOR_MOVEMENT = False
                elif key == '2':
                    setup_new_recording('falling')
                    WAITING_FOR_MOVEMENT = False
                elif key == 'q':
                    print("Exiting program...")
                    SHOULD_EXIT = True
                    break
        time.sleep(0.1)  


## Main
connect_ports()
initialize_csv_files()
listener_thread = threading.Thread(target=keyboard_listener, daemon=True)
listener_thread.start()

while not SHOULD_EXIT: 
    try:
        if ConfigFileName != None:
            send_cfg()
        parse()
    except serial.SerialTimeoutException:
        print('Data could not be read')
        time.sleep(1)
    except KeyboardInterrupt:
        if current_csvfile:
            current_csvfile.close()
        UART.close()
        sys.exit(0)

if current_csvfile:
    current_csvfile.close()
if UART:
    UART.close()
print("Program terminated.")