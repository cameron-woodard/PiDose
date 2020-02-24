"""Program for automated drug treatment of mice in the PiDose cage.

This program is meant to be run on a Raspberry Pi operating a PiDose home-cage
setup. It performs all detection, weighing, drug and water dispensing and data 
recording necessary for the proper operation of PiDose. Note that this version 
of the script does not incorporate a camera to take pictures/videos. This 
program should be run from the provided bash script (monitor.sh), which should 
be set to automatically run at startup.

Written by Cameron Woodard and Bahram Samiei.

"""

import os
import sys
import board
import busio
import adafruit_mpr121
import RPi.GPIO as GPIO
import datetime as dt
import numpy as np
from time import sleep, time
from scipy import stats
from Scale import Scale
from RFIDTagReader import TagReader


# Task Constants
RFID_GRACE_PERIOD = 30000
WEIGH_FREQUENCY = 5
WATER_TIMEOUT = 10000
DRUG_DROPS_PER_GRAM = 2
DRUG_DROP_FREQUENCY = 1
SOLENOID_OPEN_TIME = 0.1
SCALE_GRAMS_PER_UNIT = 0.00048
RETARE_WEIGH_ATTEMPTS = 20
RETARE_VARIABILITY = 0.1
UPPER_WEIGHT = 60
LOWER_WEIGHT = 20
SYRINGE_STEPS = 57

# GPIO Pin Constants
PIN_RFID_TIR = 27
PIN_SCALE_CLK = 22
PIN_SCALE_DAT = 17
PIN_CAP_IRQ = 26
PIN_SOLENOID = 6
PIN_MOTOR_STEP = 12
PIN_MOTOR_DIR = 16
PIN_MOTOR_MS1 = 23
PIN_MOTOR_MS2 = 24

# Capacitive Sensor Constants
CAP_SPOUT_PIN = 0
CAP_TOUCH_THRESHOLD = 25
CAP_RELEASE_THRESHOLD = 10

# RFID Constants 
RFID_PORT = "/dev/serial0"
RFID_TIMEOUT = 0.1
RFID_KIND = 'ID'
RFID_UNKNOWN_REBOOT = 10


# Global Mouse Variables
mouse_name = ''
mouse_day = 0
day_count = 0
drug_drops = 0
water_drops = 0
current_weight = 0
required_drug_drops = 0
water_timer = 0
current_day = dt.datetime.now().day
b_mouse_treatment = False
b_reboot_pi = False


def update_mouse_variables(rfid_tag):
    """Takes an RFID tag and sets the global mouse variables of the program to
    those corresponding with the detected mouse. 
    
    Args:
        rfid_tag is string containing the RFID.
        
    Returns:
        None.
    
    Raises:
        ValueError: rfid_tag not found in mice.cfg.
    """
    
    global mouse_name, mouse_day, day_count, drug_drops, water_drops
    global current_weight, required_drug_drops, b_mouse_treatment

    with open('/home/pi/piDose/mice.cfg', 'r') as file:
        mice_lines = file.readlines()

    for mouse_line in mice_lines:
        mouse_line = mouse_line.replace('\n', '')
        mouse_line = mouse_line.split('\t')

        if mouse_line[0] == str(rfid_tag):
            print("%s detected (ID = %s)! (%s)" %(mouse_line[1], str(rfid_tag),
                  str(dt.datetime.now())))
            mouse_name = mouse_line[1]
            if mouse_line[2] == 'DRUG':
                b_mouse_treatment = True
            mouse_day = int(mouse_line[3])
            day_count = int(mouse_line[4])
            drug_drops = int(mouse_line[5])
            water_drops = int(mouse_line[6])
            required_drug_drops = int(mouse_line[7])
            current_weight = float(mouse_line[8])
            
            # Check if it is a new day and reset daily variables if so
            if dt.datetime.now().day != mouse_day:
                # All non-mouse RFIDs used for testing/troubleshooting should 
                # have the string 'TEST' in their name 
                if not 'TEST' in mouse_name:
                    print("Rollover time reached. Calculating average weight "
                          "and resetting daily variables...")
                    n_weights, current_weight = get_average_weight()
                    print("Average weight on Day %i for %s was %s grams (mode "
                          "calculated from %i weight measurements)." %(
                          day_count, mouse_name, str(current_weight), 
                          n_weights))
                    record_summary()
                    water_drops = 0
                    if b_mouse_treatment:
                        drug_drops = 0
                        required_drug_drops = int(round(current_weight
                                                        *DRUG_DROPS_PER_GRAM))
                    day_count += 1
                mouse_day = dt.datetime.now().day
            return None
    
    raise ValueError("Mouse name not found in mice.cfg (ID = %s)." 
                     %(str(rfid_tag)))


def save_mouse_variables():
    """Writes mouse variables to mice.cfg.
    
    Args:
        None.
        
    Returns:
        None.
    """
    
    with open('/home/pi/piDose/mice.cfg', 'r') as file:
        data = file.readlines()

    for j in range(len(data)):
        data[j] = data[j].replace('\n', '')
        data[j] = data[j].split('\t')

        if data[j][1] == mouse_name:
            data[j][3] = mouse_day
            data[j][4] = day_count
            data[j][5] = drug_drops
            data[j][6] = water_drops
            data[j][7] = required_drug_drops
            data[j][8] = current_weight

    with open('/home/pi/piDose/mice.cfg', 'w') as file:
        for j in range(len(data)):
            new_line = ''
            for i in range(len(data[j])):
                new_line += str(data[j][i]) + (
                    '\n' if i == (len(data[j])-1) else '\t')
            file.write(new_line)
    
    return None


def record_event(timestamp, event):
    """Records event information to data file for current mouse.
    
    Event Codes:
        00: Mouse entered
        99: Mouse exited
        01: Mouse licked spout
        02: Mouse received water drop
        03: Mouse received drug solution drop
        
    Args:
        timestamp is a datetime.datetime() object
        event is a string containing the event code
        
    Returns:
        None.
    """
    
    with open('/home/pi/piDose/data/%s/%s_data.txt' % (mouse_name, 
              mouse_name), 'a') as file:
        data = str(timestamp) + '\t' + event + '\n'
        file.write(data)
    return None


def record_summary():
    """Records a summary of the previous day for each mouse.
    
    Args:
        None.
    
    Returns:
        None.
    """

    with open('/home/pi/piDose/data/%s/%s_summary.txt' % (mouse_name, 
              mouse_name), 'a') as summary_file:
        if day_count == 0:
            summary_file.write("Summary file for %s\n\n" %(mouse_name))
            summary_file.write("Day\tTotal Drops\tWater Drops\tDrug Drops\t"
                               "Required Drug Drops\tAverage Weight\n")
        data = (str(day_count) + '\t' + str(water_drops + drug_drops) + '\t\t' 
                + str(water_drops) + '\t\t' + str(drug_drops) + '\t\t' + 
                str(required_drug_drops) + '\t\t\t' + str(current_weight) + 
                '\n')  
        summary_file.write(data)
    return None
        
        
def get_average_weight():
    """Calculates average weight for the previous day by taking all weight 
    measurements, rounding to 0.1g and taking the mode of these values.
    
    Args:
        None.
        
    Returns:
        The number of weight recordings used to calculate the average weight
        (as an int), and the average weight (as a float).
    """
    
    with open('/home/pi/piDose/data/%s/Weights/%s_weights_day%d.txt' % (
              mouse_name, mouse_name, day_count), 'r') as weight_file:
        weight_list = []
        for line in weight_file:
            line = line.replace('\n', '')
            line = line.split('\t')
            try:
                if (float(line[1]) <= UPPER_WEIGHT and float(line[1]) >= 
                    LOWER_WEIGHT):
                    weight_list.append(round(float(line[1]), 1))
            except IndexError:
                continue
    arr = np.array(weight_list)
    weight = stats.mode(arr)
    return len(weight_list), weight[0][0]


def dispense_water(drug):
    """Dispenses either a water drop (from solenoid) or a drug solution drop
    (from syringe pump).
    
    Args:
        drug is a boolean variable which is True if the mouse should receive
        a drug drop, or False otherwise.
        
    Returns:
        None.
    """
    
    if drug:
        for x in range(SYRINGE_STEPS):
            GPIO.output(PIN_MOTOR_STEP, True)
            sleep(0.001)
            GPIO.output(PIN_MOTOR_STEP, False)
            sleep(0.001)
    else:
        GPIO.output(PIN_SOLENOID, True)
        sleep(SOLENOID_OPEN_TIME)
        GPIO.output(PIN_SOLENOID, False)
    return None


def time_ms():
    """Converts the current time since the epoch to milliseconds as an integer.
    
    Args:
        None.
        
    Returns:
        Milliseconds since the epoch as an int.   
    """
    
    ms = int(round(time() * 1000))
    return ms
    

def zero_scale(scale):
    """Checks if load cell is stable over a certain time period and then 
    re-tares it if so, otherwise does nothing.
    
    Will also trigger a reboot if it is a new day and load cell reading is 
    stable.
    
    Args:
        scale is a Scale.Scale() object representing the load cell.
        
    Returns:
        None. 
    """
    
    global b_reboot_pi
    
    weight_list = []
    weigh_timer = time_ms()
    with open('/home/pi/piDose/tare_weights.txt', 'a') as file:
        file.write(str(dt.datetime.now()) + '\n')
        while len(weight_list) < RETARE_WEIGH_ATTEMPTS:
            if time_ms() - weigh_timer >= 1000/WEIGH_FREQUENCY:
                weigh_timer = time_ms()
                weight = scale.weighOnce()
                file.write(str(weight) + '\n')
                weight_list.append(weight)
        mean_weight = sum(weight_list)/len(weight_list)
        
        # Check the variability of the weight measurements over the period
        for weight in weight_list:
            if abs(weight - mean_weight) > RETARE_VARIABILITY:
                print("Scale not zeroed, sample variability too high.")
                file.write("Not zeroed, sample variability too high. Mean "
                           "weight = " + str(round(mean_weight, 2)) + '\n')
                return None
                
        # If readings from load cell not further than RETARE_VARIABILITY away 
        # from mean weight, and day has not changed, re-zero the load cell
        if dt.datetime.now().day == current_day:
            print("Zeroing scale.")
            scale.tare(1, False)
            file.write('Scale zeroed. Mean weight = ' 
                       + str(round(mean_weight, 2)) + '\n')
            return None 
        
        # If it is past midnight on a new day and there is no mouse in the 
        # chamber, trigger an automatic reboot of the system.
        else:
            print("New day in the cage. Triggering automatic reboot of the "
                  "system (%s)." %(str(dt.datetime.now())))
            file.write("New day in the cage and low scale variability. "
                       "Automatic reboot triggered.\n")
            b_reboot_pi = True

 
def dispense_water_callback(cap):
    """Callback routine that is triggered every time a rising edge is detected
    on the capacative sensor input.
    
    Triggers delivery of a drugged or regular water drop based on the 
    specified drug timing and daily dose.
    
    Args:
        cap is a adafruit_mpr121.MPR121() object representing the capacitive
        sensor.
        
    Returns:
        None.
    """

    global water_timer, drug_drops, water_drops

    # Read off touch and record data
    cap.touched()
    record_event(dt.datetime.now(), '01')
    print("Lick detected (%s)." % (str(dt.datetime.now())))
    
    # If enough time has passed since last water drop delivery, deliver drop
    if time_ms() - water_timer >= WATER_TIMEOUT:
        water_timer = time_ms()
        timestamp = dt.datetime.now()
       
        # Dispense water or drug drops
        if (b_mouse_treatment and drug_drops < required_drug_drops and 
            (drug_drops + water_drops) % DRUG_DROP_FREQUENCY == 0):
            print("Dispensing drugged water drop.")
            record_event(timestamp, '03')
            drug_drops += 1
            dispense_water(drug=True)
            
        else:
            print("Dispensing regular water drop.")
            record_event(timestamp, '02')
            water_drops += 1
            dispense_water(drug=False)
    else:
        print("Insufficient time has passed since last drop.")
        
    return None

            
def main():
    """Initializes and runs the PiDose system.
    
    Args:
        None.
        
    Returns:
        None.
    """
    
    global b_mouse_treatment, b_reboot_pi

    # GPIO Setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_RFID_TIR, GPIO.IN)
    GPIO.setup(PIN_CAP_IRQ, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(PIN_SCALE_DAT, GPIO.IN)
    GPIO.setup(PIN_SOLENOID, GPIO.OUT)
    GPIO.output(PIN_SOLENOID, False)
    GPIO.setup(PIN_MOTOR_STEP, GPIO.OUT)
    GPIO.output(PIN_MOTOR_STEP, False)
    GPIO.setup(PIN_MOTOR_DIR, GPIO.OUT)
    GPIO.output(PIN_MOTOR_DIR, False)
    GPIO.setup(PIN_MOTOR_MS1, GPIO.OUT)
    GPIO.output(PIN_MOTOR_MS1, True)
    GPIO.setup(PIN_MOTOR_MS2, GPIO.OUT)
    GPIO.output(PIN_MOTOR_MS2, True)
    
    # Capacitive Sensor Setup
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        cap = adafruit_mpr121.MPR121(i2c)
        cap[CAP_SPOUT_PIN].threshold = CAP_TOUCH_THRESHOLD
        cap[CAP_SPOUT_PIN].release_threshold = CAP_RELEASE_THRESHOLD
    except Exception as e:
        raise e("Failed to initialize MPR121, check your wiring!")
    callback_func = lambda channel, c=cap: dispense_water_callback(c)
    
    # RFID Reader Setup
    try:
        tag_reader = TagReader(RFID_PORT, doChecksum=False, 
                              timeOutSecs=RFID_TIMEOUT, kind=RFID_KIND)
    except Exception as e:
        raise e("Error making RFIDTagReader")
    unknown_count = 0
    
    # Scale Setup
    scale = Scale(PIN_SCALE_DAT, PIN_SCALE_CLK, SCALE_GRAMS_PER_UNIT, 1)
    scale.weighOnce()
    scale.tare(1, False)
    
    # Task Variables
    b_mouse_entered = False
    weigh_timer = time_ms()
    
    print("Done initializing.")
    print("Waiting for mouse...")
    
    try:
        while True:
            
            # Reboot the system in certain circumstances
            if b_reboot_pi:
                sys.exit()
            
            # Wait for an RFID to come into range and then attempt to load the 
            # stats for that mouse
            if GPIO.input(PIN_RFID_TIR):
                if not b_mouse_entered:
                    tag_id = tag_reader.readTag()
                try:
                    update_mouse_variables(tag_id)
                except ValueError as e:
                    print(e)
                    print("Waiting for mouse to leave.")
                    while GPIO.input(PIN_RFID_TIR):
                        sleep(0.01)
                    print("Mouse no longer in range.")
                    
                    # Sometimes, for whatever reason, the RFID reader stops 
                    # working and will not successfully detect any of the mice. 
                    # Following ensures that if an unknown mouse is detected
                    # too many times, the cage will automatically restart.
                    unknown_count += 1
                    if unknown_count == RFID_UNKNOWN_REBOOT:
                        print("Too many unkown tags detected, triggering "
                              "reboot of the system (%s)." 
                              %(str(dt.datetime.now())))
                        b_reboot_pi = True
                    continue
                
                # Record entrance and activate cap sensor
                record_event(dt.datetime.now(), '00')
                b_mouse_entered = True
                cap.touched()
                GPIO.add_event_detect(PIN_CAP_IRQ, GPIO.FALLING, 
                                      callback=callback_func) 
    
                # Weigh animal until RFID goes out of range
                with open('/home/pi/piDose/data/%s/Weights/'
                          '%s_weights_day%d.txt' 
                          % (mouse_name, mouse_name, day_count), 'a') as file:
                    while True:
                        if (time_ms() - weigh_timer >= 1000/WEIGH_FREQUENCY 
                            and GPIO.input(PIN_RFID_TIR)):
                            weigh_timer = time_ms()
                            weight = scale.weighOnce()
                            weight_line = (str(dt.datetime.now()) + '\t' + 
                                           str(weight) + '\n')
                            file.write(weight_line)
                        
                        # If RFID goes out of range, start grace period and
                        # turn off cap sensor
                        if not GPIO.input(PIN_RFID_TIR):
                            grace_start = time_ms()
                            time_last_detected = dt.datetime.now()
                            GPIO.remove_event_detect(PIN_CAP_IRQ)
                            print("%s no longer detected. Beginning grace "
                                  "period... " % (mouse_name))
                            
                            # Wait for grace period to finish or for RFID to 
                            # come back in range
                            while (not GPIO.input(PIN_RFID_TIR) and time_ms() 
                                       - grace_start < RFID_GRACE_PERIOD):
                                sleep(0.01)
                            new_id = tag_reader.readTag()
                            
                            # Following is True if new mouse detected, or no
                            # RFID in range. Save data for previous mouse.
                            if tag_id != new_id:
                                save_mouse_variables()
                                record_event(time_last_detected, '99')
                                b_mouse_treatment = False
                                if new_id != 0:
                                    print("New mouse entered during grace "
                                          "period. Identifying...")
                                    tag_id = new_id
                                else:
                                    print("%s has exited the chamber (%s)." % 
                                          (mouse_name, str(dt.datetime.now())))
                                    b_mouse_entered = False
                                    zero_scale(scale)
                                break
                            
                            # Otherwise the same mouse is back in range.
                            # Reactivate cap sensor.
                            else:
                                cap.touched()
                                GPIO.add_event_detect(PIN_CAP_IRQ, 
                                    GPIO.FALLING, callback=callback_func)
                                print("%s has returned within grace period." 
                                      % (mouse_name))
            sleep(0.01)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected...")
    finally:
        if b_mouse_entered:
            save_mouse_variables()
            record_event(dt.datetime.now(), '99')
        GPIO.cleanup()
        if b_reboot_pi:
            os.system('sudo reboot')


if __name__ == '__main__':
    main()