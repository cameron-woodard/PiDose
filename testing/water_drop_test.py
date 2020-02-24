"""Script for dispensing a test water drop from the solenoid valve.

Written by Cameron Woodard
"""
import RPi.GPIO as GPIO
from time import sleep

PIN_SOLENOID = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_SOLENOID, GPIO.OUT)
GPIO.output(PIN_SOLENOID, False)

try:
    t = input("Please set a length of time to open the valve for: ")
    try:
        t = float(t)
    except ValueError:
        print("Not a valid number.")
    else:
        while True:
            input("Press enter to dispense a drop.")
            GPIO.output(PIN_SOLENOID, True)
            sleep(t)
            GPIO.output(PIN_SOLENOID, False)

except KeyboardInterrupt:
    GPIO.cleanup()
