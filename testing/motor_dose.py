"""Script for dispensing test drop from the syringe pump.

Written by Cameron Woodard
"""
import RPi.GPIO as GPIO
from time import sleep

PIN_MOTOR_STEP = 12
PIN_MOTOR_DIR = 16
PIN_MOTOR_MS1 = 23
PIN_MOTOR_MS2 = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_MOTOR_STEP, GPIO.OUT)
GPIO.setup(PIN_MOTOR_DIR, GPIO.OUT)
GPIO.setup(PIN_MOTOR_MS1, GPIO.OUT)
GPIO.setup(PIN_MOTOR_MS2, GPIO.OUT)
GPIO.output(PIN_MOTOR_STEP, False)
GPIO.output(PIN_MOTOR_DIR, False)
GPIO.output(PIN_MOTOR_MS1,True)
GPIO.output(PIN_MOTOR_MS2,True)

def spin_motor(num_steps):
    for y in range(num_steps):
        GPIO.output(PIN_MOTOR_STEP, True)
        sleep(0.001)
        GPIO.output(PIN_MOTOR_STEP, False)
        sleep(0.001)

num_steps = int(input('Please enter the number of steps: '))

try:
    while True:
        spin_motor(num_steps)
        input("Press enter to dispense another drop.")

except KeyboardInterrupt:
    GPIO.cleanup()
