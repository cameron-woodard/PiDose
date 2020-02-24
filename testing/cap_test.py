import board, busio, adafruit_mpr121
import RPi.GPIO as GPIO

PIN_CAP_IRQ = 26
count = 0
pin = 5

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_CAP_IRQ, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    i2c = busio.I2C(board.SCL, board.SDA)
    cap = adafruit_mpr121.MPR121(i2c)
    cap[pin].threshold = 12
    cap[pin].release_threshold = 6
except Exception as e:
    raise e("Failed to initialize MPR121, check your wiring!")

def capSensorISR(channel):
    global count
    cap.touched()
    count += 1
    print("Touch detected (count = %i)." %(count))

def main():
    print("This script will test the functioning of the spout capacitive sensor. Touch the spout to trigger an event detection.")
    GPIO.add_event_detect(PIN_CAP_IRQ, GPIO.FALLING, callback=capSensorISR)
    print("Touch threshold: " + str(cap[pin].threshold))
    print("Release threshold: " + str(cap[pin].release_threshold))
    while True:
        pass

try:
    main()
except KeyboardInterrupt:
    print("Touch threshold: " + str(cap[pin].threshold))
    print("Release threshold: " + str(cap[pin].release_threshold))
    print("Thanks for using me!")
    GPIO.cleanup()
