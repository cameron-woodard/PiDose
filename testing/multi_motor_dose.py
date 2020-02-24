"""Script for dispensing multiple drops of a certain step number from the 
syringe pump in order to calibrate drop size.

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

try:
    num_steps = int(input('Please enter the number of steps per drop:'))
    num_times = int(input ('Please enter the number of drops to dispense:'))
    for x in range(num_times):
        print("Drop " + str(x+1) +'.')
        spin_motor(num_steps)
        sleep(0.2)
except KeyboardInterrupt:
    GPIO.cleanup()