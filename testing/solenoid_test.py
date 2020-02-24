import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
PIN_SOLENOID = 6
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
