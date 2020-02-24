GNU nano 2.7.4                                      File: piDose_script.sh                                      

#!/bin/bash
# This script should set up all libraries required for piDose on a blank Raspberry pi.

sudo apt-get update
sudo apt-get upgrade
sudo pip3 install --upgrade setuptools

mkdir piDoseSetup
cd piDoseSetup

echo "Installing scipy, matplotlib and dependencies"
sudo pip3 install scipy
sudo pip3 install matplotlib
sudo apt-get install libatlas-base-dev

echo "Installing CircuitPython and MPR121 Libraries"
sudo pip3 install adafruit-blinka
sudo pip3 install adafruit-circuitpython-mpr121

echo "Cloning pulsedThread and building makefile"
git clone https://github.com/jamieboyd/pulsedThread.git
cd pulsedThread
sudo make
sudo make install
cd ..

echo "Cloning GPIO_Thread and setting up HX711"
git clone https://github.com/jamieboyd/GPIO_Thread.git
cd GPIO_Thread
sudo python3 HX711_setup.py install
cd ..

echo "Cloning RFID reader"
git clone https://github.com/jamieboyd/RFIDTagReader.git
cd RFIDTagReader
sudo python3 RFIDTagReader_setup.py install
cd ..

echo "Install complete"
