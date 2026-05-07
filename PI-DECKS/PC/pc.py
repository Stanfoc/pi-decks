# Welcome contributor!
# Version: InDev Demo

import serial
import time
import serial.tools.list_ports
import os

MESSAGE_TIMEOUT = 2

# Find the port with Pico on it
def find_pico():
    for port in serial.tools.list_ports.comports():
        if "Pico" in port.description or "USB Serial" in port.description or "ACM" in port.device:
            return port.device
    return None

port = find_pico()
if not port:
    # REQ: Should we exit if the pico isn't found, or just keep trying?
    print("ERROR: Pico not found! Check connection and try again.")
    exit(1)

print("Connecting to pico on: " + port)
ser = serial.Serial(port, 115200, timeout=MESSAGE_TIMEOUT)

# Function to grab lines from select services
def await_service(service, strip_service=True):
    print("Awaiting service: " + service)
    lengnth = len(service)
    # Repeatly read lines until we get the one we want, or timeout
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line:
            if line.startswith(service):
                print("Got requested line: " + service)
                    # Return the line with the service name removed and whitespace stripped, or just the line with whitespace stripped if strip_service is False
                if strip_service:
                    return line[lengnth:].strip()
                else:
                    return line.strip()
        else:
            print("Timeout while waiting for service: " + service)
            return None
        
print("Sending ping to pico...")
ser.write(b'PING\n')
ser.flush()
if await_service("PONG"):
    print("Pico is alive!")
else:
    print("Pico did not respond to ping, exiting.")
    exit(1)