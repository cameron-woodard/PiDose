import RPi.GPIO as GPIO
from time import sleep

PIN_MOTOR_STEP = 12
PIN_MOTOR_DIR = 16
PIN_MOTOR_MS1 = 23
PIN_MOTOR_MS2 = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_MOTOR_STEP, GPIO.OUT)
GPIO.setup(PIN_MOTOR_DIR, GPIO.OUT)
GPIO.setup(PIN_MOTOR_MS1, GPIO.OUT)
GPIO.setup(PIN_MOTOR_MS2, GPIO.OUT)
GPIO.output(PIN_MOTOR_STEP, False)
GPIO.output(PIN_MOTOR_DIR, False)
GPIO.output(PIN_MOTOR_MS1,True)
GPIO.output(PIN_MOTOR_MS2,True)

try:
    ans = input("Would you like to move motor forward (f) or backwards (b): ")
    if ans.lower() == 'f':
        GPIO.output(PIN_MOTOR_DIR, False)
    else:
        GPIO.output(PIN_MOTOR_DIR, True)
    input("Press enter to begin spinning motor backwards, and then CTRL-C to stop.")
    while True:
        GPIO.output(PIN_MOTOR_STEP, True)
        sleep(0.0005)
        GPIO.output(PIN_MOTOR_STEP, False)
        sleep(0.0005)
except KeyboardInterrupt:
    GPIO.cleanup()