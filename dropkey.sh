#!/bin/bash

if [ $# -lt 2 ]; then
    echo 'usage: dropkey.sh <username> <ip>'
else
    if [ ! -f pubkey ]; then
        echo 'pubkey does not exist in current dir'
    else
        scp pubkey $1@$2:~/.ssh/authorized_keys
    fi
fi
