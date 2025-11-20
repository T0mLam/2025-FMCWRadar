import threading
import struct
import serial
import numpy as np
from parse_frame import *

class convert(bytes):
    def __str__(self):
        return 'b\'{}\''.format(''.join('\\x{:02x}'.format(b) for b in self))



class UARTManager:
    def __init__(self, port, baud_rate):
        self.port = port
        self.baud_rate = baud_rate
        self.uart = None
        self.running = False
        self.thread = None
        self.on_classification_updated = None
        self.on_point_cloud_updated = None

    def connect(self):
        try:
            self.uart = serial.Serial(self.port, self.baud_rate, timeout=5)
            print(f"[UART] Connected to {self.port} at {self.baud_rate}")
            return True
        except Exception as e:
            print(f"[UART] Failed to connect: {e}")
            return False

    def close(self):
        print("[UART] Closing connection...")
        self.running = False
        if self.uart and self.uart.is_open:
            try:
                self.uart.close()
            except Exception as e:
                print(f"[UART] Error while closing: {e}")
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        print("[UART] Closed.")

    def start_parsing(self):
        if not self.uart or not self.uart.is_open:
            print("[UART] Not connected. Cannot start parsing.")
            return

        self.running = True
        self.thread = threading.Thread(target=self.parse, daemon=True)
        self.thread.start()
        print("[UART] Started parsing thread.")

    def read_all(self):
        if self.uart:
            return convert(self.uart.read_all())
        return b''

    def read(self, length):
        if self.uart:
            return convert(self.uart.read(length))
        return b''

    def parse(self):
        HEADERLENGTH = 40
        DEBUG = 0
        frameCount = 0
        OldFrameNumber = 0
        ErrorCount = 0

        print("[UART] Listening for frames...")
        while self.running:
            try:
                outputPacket = self.read_all()
                if not outputPacket:
                    print("No data yet...")
                    continue

                # Wait for magic word
                offset = outputPacket.find(UART_MAGIC_WORD)
                while offset == -1 and self.running:
                    outputPacket += self.read(len(UART_MAGIC_WORD))
                    offset = outputPacket.find(UART_MAGIC_WORD)
                if not self.running:
                    break
                outputPacket = outputPacket[offset:]

                # Read header
                outputPacket += self.read(HEADERLENGTH - len(UART_MAGIC_WORD))
                header = outputPacket[:HEADERLENGTH]
                magic, version, totalPacketLen, platform, frameNum, timeCPUCycles, numDetectedObj, numTLVs, subFrameNum = \
                    struct.unpack('Q8I', header)
                outputPacket += self.read(totalPacketLen - HEADERLENGTH)

                # Try parsing this frame
                try:
                    frameCount += 1
                    frameDict = parseStandardFrame(outputPacket, DEBUG)

                    # Debug: show frame contents to help adapt format
                    print(f"[UART] Frame #{frameCount} keys: {list(frameDict.keys())}")

                    # Classification update (if available)
                    if 'mlResult' in frameDict and frameDict['mlResult'] != "NONE":
                        confidence = int(np.max(frameDict.get('mlProbabilities', [1])) * 100)
                        if self.on_classification_updated:
                            self.on_classification_updated(frameDict['mlResult'], confidence)

                    # Handle point cloud or extended point cloud
                    if 'pointCloud' in frameDict and 'numDetectedPoints' in frameDict:
                        num_pts = frameDict['numDetectedPoints']
                        pts = frameDict['pointCloud']
                    elif 'extPointCloud' in frameDict:
                        pts = frameDict['extPointCloud']
                        num_pts = len(pts)
                    else:
                        pts = []
                        num_pts = 0

                    if num_pts > 0:
                        row = []
                        for i in range(num_pts):
                            try:
                                row.append([
                                    round(pts[i][1], 2),
                                    round(pts[i][0], 2)
                                ])
                            except Exception:
                                pass
                        if self.on_point_cloud_updated and row:
                            self.on_point_cloud_updated(np.array(row))
                    else:
                        print("[UART] No point cloud data in this frame")

                except Exception as parse_error:
                    print(f"[UART] Error in parsing frame: {parse_error}")

                # Move to next frame
                outputPacket = outputPacket[totalPacketLen:]
                if frameNum - OldFrameNumber != 1:
                    ErrorCount += 1
                    if DEBUG:
                        print(f"[UART] Frame skip detected. ErrorCount: {ErrorCount}")
                OldFrameNumber = frameNum

            except Exception as e:
                print(f"[UART] Fatal UART read error: {e}")
                break
