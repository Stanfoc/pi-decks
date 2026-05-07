print("LOG:Starting pico deck!")

from pimoroni import Button
from picographics import PicoGraphics, DISPLAY_PICO_EXPLORER
import time
import sys
import select
import machine


# Button set up
button_a = Button(12, repeat_time=500)
button_b = Button(13, repeat_time=500)
button_x = Button(14, repeat_time=500)
button_y = Button(15, repeat_time=500)

# Display set up
display = PicoGraphics(display=DISPLAY_PICO_EXPLORER)
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
RED = display.create_pen(255, 0, 0)
GREEN = display.create_pen(0, 255, 0)
BLUE = display.create_pen(0, 0, 255)
display.set_font("bitmap8")

# Other vars
armed = False
mode = 0
sunMode = False

# functions
def clearScreen(clearColor=BLACK, drawColor=WHITE):
    if sunMode and clearColor == BLACK and drawColor == WHITE:
        clearColor = WHITE
        drawColor = BLACK
    display.set_pen(clearColor)
    display.clear()
    display.set_pen(drawColor)
    display.update()

def sunColoring():
    if sunMode:
        display.set_pen(BLACK)
    else:
        display.set_pen(WHITE)

def commandSent():
    sunColoring()
    display.text("Command sent!", 25, 115, scale=3)
    display.update()
    time.sleep(0.65)
    clearScreen()


# Start up
def startUp():
    clearScreen(RED)
    display.set_pen(BLUE)
    display.text("Waiting for", 30, 60, scale=3)
    display.text("PC...", 70, 110, scale=4)
    display.update()
    print("LOG:Pico deck waiting for PC handshake...")

    # Await handshake
    while True:
        if select.select([sys.stdin], [], [], 0)[0]:
            incoming = sys.stdin.readline().strip()
            if incoming:
                print("LOG:Received handshake message: " + incoming)
                if "READY" in incoming.upper():
                    print("LOG:Handshake confirmed")
                    break
        time.sleep_ms(100)

    # Handshake successful
    clearScreen(GREEN)
    display.text("PC connected!", 20, 90, scale=3)
    display.update()
    time.sleep(0.5)

    # Sync mode
    clearScreen(BLUE)
    display.text("Syncing...", 70, 110, scale=2)
    display.update()

    print("LOG:Syncing mode with PC.")
    print("SYNC: ", mode)

    while True:
        if select.select([sys.stdin], [], [], 0)[0]:
            incoming = sys.stdin.readline().strip()
            if incoming:
                print("LOG:PC said: " + incoming)
                if incoming.strip() == str(mode):
                    print("LOG:Mode synced!")
                    break
        time.sleep(0.15)

    clearScreen()


# Main program
startUp()

heartbeat_interval = 10   # send ping every 10 seconds
timeout = 15              # disconnect after 25 seconds of silence
last_heartbeat = time.time()
last_heartbeat_msg = time.time()
poll_timeout = 0.15

print("LOG:Pico deck ready!")

while True:
    try:

        if mode == 0:
            display.set_pen(RED)
            display.text("YT", 5, 50, scale=6)

            display.set_pen(BLUE)
            display.text("DC", 5, 165, scale=6)

            display.set_pen(BLUE)
            display.text("STEAM", 130, 50, scale=4)

            display.set_pen(GREEN)
            display.text("OTHER", 130, 175, scale=4)

            if button_a.read():
                print("CMD:OPEN_YOUTUBE")
                commandSent()

            if button_b.read():
                print("CMD:OPEN_DISCORD")
                commandSent()

            if button_x.read():
                print("CMD:OPEN_STEAM")
                commandSent()

            if button_y.read():
                print("CMD:MODE_1")
                mode = 1
                clearScreen()

        elif mode == 1:
            display.set_pen(RED)
            display.text("SUN", 5, 50, scale=6)

            display.set_pen(BLUE)
            display.text("SONG", 5, 165, scale=4)

            display.set_pen(BLUE)
            display.text("HB", 140, 50, scale=4)

            display.set_pen(GREEN)
            display.text("MAIN", 130, 175, scale=4)

            if button_a.read():
                print("LOG:Sun mode toggle requested")

                if sunMode:
                    sunMode = False
                    print("LOG:Sun mode OFF")
                else:
                    sunMode = True
                    print("LOG:Sun mode ON")

                sunColoring()
                display.text("Command sent!", 25, 115, scale=3)
                display.update()
                time.sleep(0.65)
                clearScreen()

            if button_b.read():
                print("CMD:MODE_2")
                mode = 2
                clearScreen()

            if button_x.read():
                print("PING")
                commandSent()

            if button_y.read():
                print("CMD:MODE_0")
                mode = 0
                clearScreen()

        elif mode == 2:
            display.set_pen(RED)
            display.text("YTM", 5, 50, scale=4)

            sunColoring()
            display.text("RICK", 5, 165, scale=5)

            display.set_pen(BLUE)
            display.text("FART", 140, 50, scale=4)

            display.set_pen(GREEN)
            display.text("MAIN", 130, 175, scale=4)

            if button_a.read():
                print("CMD:OPEN_YTM")
                commandSent()

            if button_b.read():
                print("CMD:PLAY_RICK")
                commandSent()

            if button_x.read():
                print("CMD:PLAY_FART")

            if button_y.read():
                print("CMD:MODE_0")
                mode = 0
                clearScreen()

        display.update()
        time.sleep(0.02)

        now = time.time()

        if now - last_heartbeat >= heartbeat_interval:
            last_heartbeat = now
            print("PING")

        readable, _, _ = select.select([sys.stdin], [], [], poll_timeout)

        if readable:
            incoming = sys.stdin.readline().strip()

            if incoming:
                last_heartbeat_msg = time.time()
                print("LOG:Heartbeat got:", incoming)

        if time.time() - last_heartbeat_msg > timeout:
            print("LOG:Heartbeat got no message")

            sunColoring()
            display.text("Lost connection...", 25, 115, scale=3)
            display.update()

            time.sleep(0.65)

            clearScreen()
            startUp()

            last_heartbeat = time.time()
            last_heartbeat_msg = time.time()

    except Exception as e:
        print("LOG:Exception, restarting handshake...")
        time.sleep(1)
        machine.reset()
