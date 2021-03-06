"""Script for delivering multiple water drops with the solenoid valve in order
to calibrate water drop size.

Written by Cameron Woodard
"""
import RPi.GPIO as GPIO
from time import sleep

PIN_SOLENOID = 6
REVERSE_SOLENOID = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_SOLENOID, GPIO.OUT)
if not REVERSE_SOLENOID:
    GPIO.output(PIN_SOLENOID, False)
else:
    GPIO.output(PIN_SOLENOID, True)

print("This script will dispense multiple water drops at the desired drop "
      "size.")

try:
    x = input("Please enter the number of drops to dispense: ")
    t = input("Please set a length of time to open the valve for each drop: ")
    try:
        t = float(t)
        x = int(x)
    except ValueError:
        print("Inputs not valid.")
    else:
        input("Press enter to dispense %i drops with a %f second valve open "
              "time." %(x, t))
        if not REVERSE_SOLENOID:
            for y in range(x):
                print("Drop " + str(y+1) +'.')
                GPIO.output(PIN_SOLENOID, True)
                sleep(t)
                GPIO.output(PIN_SOLENOID, False)
                sleep(0.2)
        else:
            for y in range(x):
                print("Drop " + str(y+1) +'.')
                GPIO.output(PIN_SOLENOID, False)
                sleep(t)
                GPIO.output(PIN_SOLENOID, True)
                sleep(0.2)

except KeyboardInterrupt:
    GPIO.cleanup()