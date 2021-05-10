#!/bin/bash

# watch script for zmNotify.py

n=$(ps aux | grep zmNotify.py | egrep -v grep | wc -l)
logFile="/tmp/zmNotifyWatch.log"

if [ "$n" -lt 1 ]
then
    echo "$(date '+%Y-%m-%d %H:%M:%S') Not Running. Starting..." >> $logFile
    /home/$USER/zmNotify/zmNotify.py &
fi
