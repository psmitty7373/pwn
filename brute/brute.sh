#!/bin/bash

if [ $# -lt 2 ]; then
    echo 'usage: brute.sh <username> <proto://ip>'
else
    hydra -t 24 -P passwords.txt -l $1 $2
fi
