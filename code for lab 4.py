# SED1115 - Lab 4: UART Chat
# Author: Abdul Ahad,ABDULELAH,CLAIRE
#
# This program lets two Picos send chat messages to each other.
# Both Picos run this same program.
#
# The program repeats 3 steps forever:
#   Step 1: If the other Pico sent us something, show it on the screen
#   Step 2: If I typed a message and pressed Enter, send it
#   Step 3: If I haven't sent anything in 5 seconds, send my time
#           (this is the "keep alive" message)

from machine import UART, Pin
import time
import sys
import select


# ----- Set up the UART (the wire connection to the other Pico) -----
# The expansion board uses UART number 1.
# TX (send) is on pin 8, RX (receive) is on pin 9.
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(bits=8, parity=None, stop=1)


# ----- Set up the keyboard -----
# These 2 lines let us check if a key was typed WITHOUT stopping
# the program to wait. (Regular input() would stop and wait.)
keyboard = select.poll()
keyboard.register(sys.stdin, select.POLLIN)


# ----- Variables -----
my_message = ""                  # the letters I have typed so far
last_send_time = time.time()     # the time (in seconds) when I last sent something


print("Chat started! Type a message and press Enter to send it.")


while True:

    # ---------- Step 1: Check for messages from the other Pico ----------
    if uart.any():                   # did anything arrive?
        data = uart.read()           # read what arrived

        if data is not None:         # make sure we really got something
            try:
                text = data.decode()          # turn the bytes into normal text
                print("Partner:", text)
            except:
                print("Received some messy data, skipping it")


    # ---------- Step 2: Check if I typed something ----------
    if keyboard.poll(0):             # was a key pressed?
        letter = sys.stdin.read(1)   # get that one key

        if letter == "\n" or letter == "\r":     # Enter key was pressed
            if my_message != "":                 # don't send empty messages
                uart.write(my_message)           # send it to the other Pico
                print("You:", my_message)
                my_message = ""                  # clear it for the next message
                last_send_time = time.time()     # remember when I sent it
        else:
            my_message = my_message + letter     # add the letter to my message


    # ---------- Step 3: Send a keep-alive if I've been quiet for 5 seconds ----------
    if time.time() - last_send_time >= 5:
        t = time.localtime()                     # get the current time
        now = str(t[3]) + ":" + str(t[4]) + ":" + str(t[5])   # hours:minutes:seconds
        uart.write("Keep alive - my time is " + now)
        last_send_time = time.time()


    # Small pause so the loop doesn't run too fast
    time.sleep(0.1)
