#!/bin/bash

cd /home/pi/piDose/
until python3 -u piDose.py &>>log.txt; do
	echo "'piDose program' crashed with exit code $?. Restarting..." >&2
	sleep 1
done