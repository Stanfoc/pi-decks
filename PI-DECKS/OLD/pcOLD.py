import serial
import time
import serial.tools.list_ports
import os

mode = 999

# Find the port with Pico on it
def find_pico():
    for port in serial.tools.list_ports.comports():
        if "Pico" in port.description or "USB Serial" in port.description or "ACM" in port.device:
            return port.device
    return None

port = find_pico()
if not port:
    print("ERROR: Pico not found! Check connection and try again.")
    exit(1)

print("Connecting to pico on: " + port)
ser = serial.Serial(port, 115200, timeout=1)

print("WARNING: Only run this program once pico deck is on the waiting for PC screen.")
print("Sending ready message to Pico deck...")
ser.write(b"READY\n")
ser.flush()
time.sleep(0.15)

# --- Sync phase ---
try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()

            if line.startswith("LOG:"):
                print("[PICO]", line[4:])
                continue

            if line:
                print("Received: " + line)

                if "SYNC:" in line:
                    # Convert mode to integer right away
                    try:
                        mode = int(line.split(":")[1].strip())
                    except ValueError:
                        print("ERROR: Could not parse SYNC mode from Pico:", line)
                        continue

                    print("Mode set to:", mode)

                    ser.write((str(mode) + "\n").encode())
                    ser.flush()

                    print("Mode confirm sent to Pico")
                    break
                else:
                    print("Wanted SYNC service but got: " + line)

except Exception as e:
    print("LOG: Exception during SYNC phase:", e)

print(mode)
print("Listening for Pico commands! (Ctrl+C to stop)")

try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()

            if line.startswith("LOG:"):
                print("[PICO]", line[4:])
                continue

            if line:
                print("Received: " + line)

                if line.startswith("PING"):
                    ser.write(b"PONG\n")
                    ser.flush()
                
                elif line.startswith("CMD:"):
                    cmd = line[4:]

                    # Check what mode the Pico is on
                    if cmd == "MODE_0":
                        mode = 0
                    elif cmd == "MODE_1":
                        mode = 1
                    elif cmd == "MODE_2":
                        mode = 2
                    elif cmd == "MODE_3":
                        mode = 3

                    # Only check for command
                    if mode == 0:
                        if cmd == "OPEN_YOUTUBE":
                            print("Opening: YOUTUBE")
                            os.startfile("https://www.youtube.com")
                        if cmd == "OPEN_STEAM":
                            print("Opening: STEAM")
                            os.startfile("steam://open/main")
                        if cmd == "OPEN_DISCORD":
                            print("Opening: DISCORD")
                            os.startfile("discord://")

                    elif mode == 1:
                        pass
                    elif mode == 2:
                        if cmd == "PLAY_SHADOWBRINGER":
                            print("Playing: SHADOWBRINGERS")
                            os.startfile("https://youtu.be/yJUP-VWgfAA?si=rR1m_hRXdLoQmaVG")
                        if cmd == "PLAY_RICK":
                            print("Playing: RICKROLL")
                            os.startfile("https://youtu.be/hB7CDrVnNCs?si=5K5BeG2dulYAx2iO")
                        if cmd == "PLAY_FART":
                            print("Playing: FART SFX")
                            os.startfile("https://youtu.be/Q_9VMaX61nI?si=GKx4J-74opfvauFH")
                            
                    elif mode == 3:
                        pass
                else:
                    print("Wanted CMD service but got: " + line)
        

        time.sleep(0.005)

except KeyboardInterrupt:
    print("Stopped by user")
finally:
    ser.close()
