# PiDose

PiDose is an open-source tool for long-term oral drug administration to mice. A 3D-printed chamber is mounted adjacent to a mouse home-cage, allowing animals free access 24 hours/day. Inside, they are individually identified by an implanted RFID capsule and are weighed by a load cell (on which the chamber is mounted). Mice learn to lick at a spout inside the chamber which delivers either water or drug solution depending on if they have received the correct drug dosage for the day.

# Files:

piDose.py - Main script required to run the PiDose cage.

monitor.sh - Bash script which should be used to run piDose.py. This script will log all output of PiDose to a file called log.txt and will restart the program should it quit due to an error. This script should be set to run on boot through a crontab task.

mice.cfg - This file maps each RFID to a mouse name, and stores a daily log of water drops, drug drops and bodyweight for each animal. Should be edited before the start of testing to include the RFIDs for each mouse to be tested.

piDose_setup.sh - Bash script which will install all libraries required to run PiDose on the Raspberry Pi.

The testing folder contains a variety of small programs to test or calibrate different components of the cage.
