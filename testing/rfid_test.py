"""Script for testing the RFID reader.

Written by Cameron Woodard
"""

from RFIDTagReader import TagReader
import RPi.GPIO as GPIO
import serial
from time import sleep

RFID_PORT = "/dev/serial0"
RFID_TIMEOUT = 0.1
RFID_KIND = 'ID'
PIN_RFID_TIR = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_RFID_TIR, GPIO.IN)


try:
    tag_reader = TagReader(RFID_PORT, doChecksum=False, 
                              timeOutSecs=RFID_TIMEOUT, kind=RFID_KIND)
except serial.serialutil.SerialException:
    print ('Error making RFID reader.')

b_tagGone = True
print('Place a tag next to reader to test detection.')
try:
    while True:
        if GPIO.input(PIN_RFID_TIR) == True and b_tagGone:
            tag = tag_reader.readTag()
            print('RFID tag detected: ', tag)
            b_tagGone = False
        elif GPIO.input(PIN_RFID_TIR) == False and not b_tagGone:
            print('RFID no longer detected.')
            b_tagGone = True
        sleep(0.01)
except KeyboardInterrupt:
    GPIO.cleanup()