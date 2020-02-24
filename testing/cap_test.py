"""Script for testing function of the spout capacitive sensor.

Written by Cameron Woodard
"""
import board
import busio
import adafruit_mpr121
import RPi.GPIO as GPIO

PIN_CAP_IRQ = 26
CAP_SPOUT_PIN = 0
CAP_TOUCH_THRESHOLD = 25
CAP_RELEASE_THRESHOLD = 10
count = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_CAP_IRQ, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    i2c = busio.I2C(board.SCL, board.SDA)
    cap = adafruit_mpr121.MPR121(i2c)
    cap[CAP_SPOUT_PIN].threshold = CAP_TOUCH_THRESHOLD
    cap[CAP_SPOUT_PIN].release_threshold = CAP_RELEASE_THRESHOLD
except Exception as e:
    raise e("Failed to initialize MPR121, check your wiring!")

def cap_sensor_callback(channel):
    global count
    cap.touched()
    count += 1
    print("Touch detected (count = %i)." %(count))

try:
    print("This script will test the functioning of the spout capacitive sensor. Touch the spout to trigger an event detection.")
    GPIO.add_event_detect(PIN_CAP_IRQ, GPIO.FALLING, callback=cap_sensor_callback)
    while True:
        pass

except KeyboardInterrupt:
    GPIO.cleanup()
