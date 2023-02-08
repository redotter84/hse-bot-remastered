#!/bin/sh

python3 ./bot.py &
python3 ./request_functions.py &
while true ; do sleep 42 ; done
