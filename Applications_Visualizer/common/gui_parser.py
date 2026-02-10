# Standard Imports
import serial
import time
import datetime
import json_fix # import this anytime before the JSON.dumps gets called
import json
import numpy
import os
json.fallback_table[numpy.ndarray] = lambda array: array.tolist()

# Logger
import logging
log = logging.getLogger(__name__)

# Local Imports
from parseFrame import *
from demo_defines import *

UART_MAGIC_WORD = bytearray(b'\x02\x01\x04\x03\x06\x05\x08\x07')

# Initialize this Class to create a UART Parser. Initialization takes one argument:
# The gui this is packaged with calls this every frame period.
# readAndParseUart() will return all radar detection and tracking information.
class UARTParser():
    def __init__(self,type):
        # Set this option to 1 to save UART output from the radar device
        self.saveBinary = 0
        self.replay = 0
        self.binData = bytearray(0)
        self.uartCounter = 0
        self.framesPerFile = 100
        self.first_file = True
        self.filepath = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        self.isLowPowerDevice = False
        self.cfg = ""
        self.demo = DEMO_OOB_x432
        self.device = "xWRL6432"
        self.frames = [] # TODO this needs to be reset if connection is reset
        self.comError = 0
        
        # Data storage
        self.now_time = datetime.datetime.now().strftime('%Y%m%d-%H%M')

        # Data logging 
        self.saveData = 0
        self.dataCounter = 0
    
        self.dataFrames = []
        self.dataFileBaseName = "data"
        self._lastDataBaseName = "data"
        self.dataSessionIdx = 0

        self.recordingStartMs = None
        self.recordingEndMs = None

        # Run gait model
        self.enable_gait_model = False
        
    def setDataFileBaseName(self, base: str):
        # reset numbering if base changes
        if base != self._lastDataBaseName:
            self._lastDataBaseName = base
            self.dataSessionIdx = 0  

        self.dataFileBaseName = base

    #Flush data to file
    def flush_data(self):
        dir = os.path.join("binData", self.filepath)
        os.makedirs(dir, exist_ok=True)
        json_name = os.path.join(dir, f"{self.dataSession}.json")
        payload = {
            "startTimestamp": self.microDopplerStartMs,
            "endTimestamp": self.microDopplerEndMs,
            "cfg": self.cfg,
            "demo": self.demo,
            "device": self.device,
            "data": self.dataFrames
        }
        with open(json_name, "w") as f:
            f.write(json.dumps(payload, indent = 4))
        self.dataFrames = []
    
    #Set save data flag in class
    def setSaveData(self, new_saveData):
        if new_saveData == 1 and self.saveData != 1:
            self.setDataFileBaseName(self.dataFileBaseName)
            self.dataSessionIdx += 1
            self.dataSession = f"{self.dataFileBaseName}_{self.dataSessionIdx}"
            self.dataCounter = 0
            self.dataFrames = []
            self.microDopplerStartMs = int(time.time() * 1000)
            self.microDopplerEndMs = None

        if new_saveData != 1 and self.saveData == 1:
            self.microDopplerEndMs = int(time.time() * 1000)
            self.flush_data()

        self.saveData = new_saveData

    #Save data dictionary to the class storage variable 
    def save_data(self, outputDict: dict):
        if self.saveData != 1:
            return

        self.dataCounter += 1
        self.dataFrames.append({
            "timestamp": time.time() * 1000,
            "frameData": outputDict
        })
    
    # This function is identical to the readAndParseUartDoubleCOMPort function, but it's modified to work for SingleCOMPort devices in the xWRLx432 family
    def readAndParseUartSingleCOMPort(self):
        # Reopen CLI port
        if(self.cliCom.isOpen() == False):
            log.info("Reopening Port")
            self.cliCom.open()

        self.fail = 0
        if (self.replay):
            return self.replayHist()

        data = {'cfg': self.cfg, 'demo': self.demo, 'device': self.device}
    
        # Find magic word, and therefore the start of the frame
        index = 0
        magicByte = self.cliCom.read(1)
        frameData = bytearray(b'')
        while (1):
            # If the device doesn't transmit any data, the COMPort read function will eventually timeout
            # Which means magicByte will hold no data, and the call to magicByte[0] will produce an error
            # This check ensures we can give a meaningful error
            if (len(magicByte) < 1):
                log.error("ERROR: No data detected on COM Port, read timed out")
                log.error("\tBe sure that the device is in the proper SOP mode after flashing with the correct binary, and that the cfg you are sending is valid")
                magicByte = self.cliCom.read(1)

            # Found matching byte
            elif (magicByte[0] == UART_MAGIC_WORD[index]):
                index += 1
                frameData.append(magicByte[0])
                if (index == 8): # Found the full magic word
                    break
                magicByte = self.cliCom.read(1)
                
            else:
                # When you fail, you need to compare your byte against that byte (ie the 4th) AS WELL AS compare it to the first byte of sequence
                # Therefore, we should only read a new byte if we are sure the current byte does not match the 1st byte of the magic word sequence
                if (index == 0):
                    magicByte = self.cliCom.read(1)
                index = 0 # Reset index
                frameData = bytearray(b'') # Reset current frame data
        
        # Read in version from the header
        versionBytes = self.cliCom.read(4)
        
        frameData += bytearray(versionBytes)

        # Read in length from header
        lengthBytes = self.cliCom.read(4)
        frameData += bytearray(lengthBytes)
        frameLength = int.from_bytes(lengthBytes, byteorder='little')
        
        # Subtract bytes that have already been read, IE magic word, version, and length
        # This ensures that we only read the part of the frame in that we are lacking
        frameLength -= 16 

        # Read in rest of the frame
        frameData += bytearray(self.cliCom.read(frameLength))

        # frameData now contains an entire frame, send it to parser
        outputDict = parseStandardFrame(frameData, self.demo, self.enable_gait_model)

        if self.saveData == 1:
                self.save_data(outputDict)
        # If save binary is enabled
        if(self.saveBinary == 1):
            self.binData += frameData
            # Save data every framesPerFile frames
            self.uartCounter += 1

        return outputDict

    # Separate connectComPort (not PortS) for xWRL6432 because it only uses one port
    def connectComPort(self, cliCom, cliBaud=115200):
        # Longer timeout time for xWRL6432 to support applications with low power / low update rate
        self.cliCom = serial.Serial(cliCom, cliBaud, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=.6)
        self.cliCom.reset_output_buffer()
        log.info('Connected (one port) with baud rate ' + str(cliBaud))
        self.isLowPowerDevice = True

    #send cfg over uart
    def sendCfg(self, cfg):
        # Remove empty lines from the cfg
        cfg = [line for line in cfg if line != '\n']
        # Ensure \n at end of each line
        cfg = [line + '\n' if not line.endswith('\n') else line for line in cfg]
        # Remove commented lines
        cfg = [line for line in cfg if line[0] != '%']

        for line in cfg:
            time.sleep(.03) # Line delay

            if(self.cliCom.baudrate == 1250000):
                for char in [*line]:
                    time.sleep(.001) # Character delay. Required for demos which are 1250000 baud by default else characters are skipped
                    self.cliCom.write(char.encode())
            else:
                self.cliCom.write(line.encode())
                
            ack = self.cliCom.readline()
            if(len(ack) == 0): # Check if the device is in flashing mode
                log.error("ERROR: No data detected on COM Port, read timed out")
                log.error("\tBe sure that the device is in the proper SOP mode after flashing with the correct binary, and that the cfg you are sending is valid")
                self.comError = 1
                return
            
            print(ack, flush=True)

            ack = self.cliCom.readline()
            print(ack, flush=True)

            if (self.isLowPowerDevice):
                ack = self.cliCom.readline()
                print(ack, flush=True)
                ack = self.cliCom.readline()
                print(ack, flush=True)

            splitLine = line.split()
            if(splitLine[0] == "baudRate"): # The baudrate CLI line changes the CLI baud rate on the next cfg line to enable greater data streaming off the xWRL device.
                try:
                    self.cliCom.baudrate = int(splitLine[1])
                except:
                    log.error("Error - Invalid baud rate")
                    sys.exit(1)
        # Give a short amount of time for the buffer to clear
        time.sleep(0.03)
        self.cliCom.reset_input_buffer()
        # NOTE - Do NOT close the CLI port because 6432 will use it after configuration

    #send single command to device over UART Com.
    def sendLine(self, line):
        if(self.cliCom.baudrate == 1250000):
            for char in [*line]:
                time.sleep(.001) # Character delay. Required for demos which are 1250000 baud by default else characters are skipped
                self.cliCom.write(char.encode())
        else:
            self.cliCom.write(line.encode())
        ack = self.cliCom.readline()
        if(len(ack) == 0): #check if the device is in flashing mode
            log.error("ERROR: No data detected on COM Port, read timed out")
            log.error("\tBe sure that the device is in the proper SOP mode after flashing with the correct binary, and that the cfg you are sending is valid")
            self.comError = 1
            return
        else:
            print(ack)
            ack = self.cliCom.readline()
            print(ack)
 