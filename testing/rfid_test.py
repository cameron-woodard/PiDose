# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 10:10:55 2019

@author: woody
"""

from RFIDTagReader import TagReader
import RPi.GPIO as GPIO, serial, time

RFID_serialPort = '/dev/serial0'
RFID_kind = 'ID'
RFID_timeout = 1
RFID_doCheckSum = False
g_RFID = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(g_RFID, GPIO.IN)


try:
    tagReader = TagReader (RFID_serialPort, RFID_doCheckSum, timeOutSecs = RFID_timeout, kind=RFID_kind)
except serial.serialutil.SerialException:
    print ('Error making RFID reader.')

b_tagGone = True
print('Place a tag next to reader to test detection.')
try:
    while True:
        if GPIO.input(g_RFID) == True and b_tagGone:
            tag = tagReader.readTag()
            print('RFID tag detected: ', tag)
            b_tagGone = False
        elif GPIO.input(g_RFID) == False and not b_tagGone:
            print('RFID no longer detected.')
            b_tagGone = True
        time.sleep(0.01)
except KeyboardInterrupt:
    print ('Quitting...')
finally:
    GPIO.cleanup()
