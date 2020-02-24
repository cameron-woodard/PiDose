# PiDose

PiDose is an open-source tool for long-term oral drug administration to mice. A 3D-printed chamber is mounted adjacent to a mouse home-cage, allowing animals free access 24 hours/day. Inside, they are individually identified by an implanted RFID capsule and are weighed by a load cell (on which the chamber is mounted). Mice learn to lick at a spout inside the chamber which delivers either water or drug solution depending on if they have received the correct drug dosage for the day. All components are controlled by a script running on a Raspberry Pi.

# Files

piDose.py - Main script required to run the PiDose cage.

monitor.sh - Bash script which should be used to run piDose.py. This script will log all output of PiDose to a file called log.txt and will restart the program should it quit due to an error. This script should be set to run on boot through a crontab task.

mice.cfg - This file maps each RFID to a mouse name, and stores a daily log of water drops, drug drops and bodyweight for each animal. Should be edited before the start of testing to include the RFIDs for each mouse to be tested.

piDose_setup.sh - Bash script which will install all libraries required to run PiDose on the Raspberry Pi.

The testing folder contains a variety of small programs to test or calibrate different components of the cage.

# PiDose Constants

RFID_GRACE_PERIOD – Time in milliseconds after RFID goes out of range of reader before program saves data for mouse and attempts to re-tare the load cell.

WEIGHT_FREQUENCY – Frequency in Hz of weight sampling from load cell.

WATER_TIMEOUT – Minimum time in milliseconds between drop deliveries.

DRUG_DROPS_PER_GRAM – Number of 10uL drug drops to be given per gram of mouse bodyweight.

DRUG_DROP_FREQUENCY – Frequency with which to deliver a drug drop (1 per every x total drops). If this is set to 1, it will deliver only drug drops until the required daily dosage is reached.

SOLENOID_OPEN_TIME – Duration in seconds to open solenoid valve for (to deliver water).

SCALE_GRAMS_PER_UNIT – Grams per load cell unit.

RETARE_WEIGH_ATTEMPTS – Number of readings taken from load cell before taring.

RETARE_VARIABILITY – Maximum variability in grams permitted of load cell reading before it will re-tare. For example, if this is set to 0.1, no load cell reading prior to taring can be greater than ±0.1 from the mean of all the readings.

UPPER_WEIGHT – Upper weight in grams used for calculating average. All weights above this are discarded.

LOWER_WEIGHT – Lower weight in grams used for calculating average. All weights below this are discarded.

SYRINGE_STEPS – Number of steps moved by the stepper motor to deliver a drop of drug solution.

PIN_RFID_TIR – Tag in range GPIO pin for RFID.

PIN_SCALE_CLK – Clock GPIO pin for the load cell.

PIN_SCALE_DAT – Data GPIO pin for the load cell.

PIN_CAP_IRQ – Interrupt GPIO pin for the load cell.

PIN_SOLENOID – Solenoid GPIO pin.

PIN_MOTOR_STEP – Syringe pump step trigger GPIO pin.

PIN_MOTOR_DIR – Syringe pump motor direction GPIO pin.

PIN_MOTOR_MS1 – Syringe pump microstep resolution GPIO pin 1.

PIN_MOTOR_MS2 – Syringe pump microstep resolution GPIO pin 2.

CAP_SPOUT_PIN – Spout pin on the MPR121 breakout.

CAP_TOUCH_THRESHOLD – Touch threshold for capacitive sensor.

CAP_RELEASE_THRESHOLD – Release threshold for capacitive sensor.

RFID_PORT – Serial port address for the RFID.

RFID_TIMEOUT – Time that reader will wait to receive full RFID.

RFID_KIND – Type of RFID reader.

RFID_UNKNOWN_REBOOT – Number of times an unknown RFID can be detected before the system reboots as a precaution.
