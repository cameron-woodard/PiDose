"""Script for graphing raw signals from the capacitive sensor.

Written by Cameron Woodard
"""

import board, busio, adafruit_mpr121, time, sys
import matplotlib.pyplot as plt

CAP_SPOUT_PIN = 0
CAP_TOUCH_THRESHOLD = 25
CAP_RELEASE_THRESHOLD = 10
filtered_values = []
baseline_values = []

try:
    i2c = busio.I2C(board.SCL, board.SDA)
    cap = adafruit_mpr121.MPR121(i2c)
    cap[CAP_SPOUT_PIN].threshold = CAP_TOUCH_THRESHOLD
    cap[CAP_SPOUT_PIN].release_threshold = CAP_RELEASE_THRESHOLD
except Exception as e:
    raise e("Failed to initialize MPR121, check your wiring!")

print("Collecting cap data. Press CTRL-C to exit and graph raw values.")
last_touched = cap.touched()
time.sleep(0.1)

try:
    while True:
        current_touched = cap.touched()
        pin_bit = 1 << CAP_SPOUT_PIN
        if current_touched & pin_bit and not last_touched & pin_bit:
            print('{0} touched!'.format(CAP_SPOUT_PIN))
        if not current_touched & pin_bit and last_touched & pin_bit:
            print('{0} released!'.format(CAP_SPOUT_PIN))
        last_touched = current_touched
        filtered_values.extend([cap.filtered_data(CAP_SPOUT_PIN)])
        baseline_values.extend([cap.baseline_data(CAP_SPOUT_PIN)])
        time.sleep(0.1)

except KeyboardInterrupt:
    plt.plot(filtered_values, 'r--')
    plt.plot(baseline_values, 'bs')
    plt.show()
    sys.exit()