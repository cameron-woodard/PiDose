"""Script to open and close the water solenoid valve.

Written by Cameron Woodard
"""

import RPi.GPIO as GPIO

PIN_SOLENOID = 6
REVERSE_SOLENOID = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_SOLENOID, GPIO.OUT)
if not REVERSE_SOLENOID:
    GPIO.output(PIN_SOLENOID, False)
else:
    GPIO.output(PIN_SOLENOID, True)

try:
    while True:
        input("Solenoid valve is closed. Press enter to open the solenoid.")
        if not REVERSE_SOLENOID:
            GPIO.output(PIN_SOLENOID, True)
        else:
            GPIO.output(PIN_SOLENOID, False)
        input("Solenoid valve is open. Press enter to close the solenoid.")
        if not REVERSE_SOLENOID:
            GPIO.output(PIN_SOLENOID, False)
        else:
            GPIO.output(PIN_SOLENOID, True)

except KeyboardInterrupt:
    GPIO.cleanup()
