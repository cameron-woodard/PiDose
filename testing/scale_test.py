"""Script for testing the load cell and grams per unit constant.

Written by Cameron Woodard
"""

from time import sleep
from Scale import Scale
import RPi.GPIO as GPIO

PIN_SCALE_CLK = 22
PIN_SCALE_DAT = 17
GRAMS_PER_UNIT = 0.000478
THREAD_ARRAY_SIZE = 80

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_SCALE_DAT, GPIO.IN)

scale = Scale(PIN_SCALE_DAT, PIN_SCALE_CLK, GRAMS_PER_UNIT, THREAD_ARRAY_SIZE)
scale.weighOnce()
scale.tare(10, False)

input("This script will help determine if the scale is working properly by "
      "outputing a raw reading from the load cell every 0.5s. Press enter "
      "when ready.")

try:
    count = 0
    while True:
        print("Load cell reading (%i): %f" %(count, scale.weighOnce()))
        sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()
