"""Script to open and close the water solenoid valve.

Written by Cameron Woodard
"""

import RPi.GPIO as GPIO

PIN_SOLENOID = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_SOLENOID, GPIO.OUT)
GPIO.output(PIN_SOLENOID, False)

try:
    while True:
        input("Press enter to open the water solenoid.")
        GPIO.output(PIN_SOLENOID, True)
        input("Press enter to close the water solenoid.")
        GPIO.output(PIN_SOLENOID, False)

except KeyboardInterrupt:
    GPIO.cleanup()
