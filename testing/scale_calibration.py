from Scale import Scale
import RPi.GPIO as GPIO

PIN_SCALE_CLK = 22
PIN_SCALE_DAT = 17

try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_SCALE_DAT, GPIO.IN)
    
    GRAMS_PER_UNIT = 1
    THREAD_ARRAY_SIZE = 80
    scale = Scale(PIN_SCALE_DAT, PIN_SCALE_CLK, GRAMS_PER_UNIT, THREAD_ARRAY_SIZE)
    scale.weighOnce()
    scale.tare(10, False)
    
    test_weight = float(input("Please input the test weight in grams: "))
    input("Please place the test weight on the scale then press enter.")
    print("Calibrating scale...")
    
    GRAMS_PER_UNIT = test_weight/scale.weigh(80)
    print("Grams per unit constant: " + str(GRAMS_PER_UNIT))
    print("Test weight in grams: " + str(GRAMS_PER_UNIT*scale.weighOnce()))


except KeyboardInterrupt:
    GPIO.cleanup()