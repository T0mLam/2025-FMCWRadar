# uart_check.py
import serial
import time
import binascii

PORT = "COM5"       # Data port
BAUD = 1250000      # Matches your config baudRate
TIMEOUT = 0.5

try:
    with serial.Serial(PORT, BAUD, timeout=TIMEOUT) as ser:
        print(f"Listening on {PORT} at {BAUD} baud...")
        start = time.time()
        count = 0
        while time.time() - start < 5:  # listen for 5 seconds
            data = ser.read(ser.in_waiting or 1)
            if data:
                count += len(data)
                print(f"Received {len(data)} bytes: {binascii.hexlify(data[:16])} ...")
        print(f"Total bytes received: {count}")
except Exception as e:
    print(f"Error: {e}")
