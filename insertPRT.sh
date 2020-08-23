#!/bin/sh

date=`date '+%Y-%m-%d-%H:%M'`

echo "==="`date '+%Y-%m-%d-%H:%M:%S'`"===="
python3 /home/ubuntu/bin/insertPRT.py
echo "==="`date '+%Y-%m-%d-%H:%M:%S'`"===="

exit
