#!/bin/bash
autossh -M 0 -i level5.key -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -R 0.0.0.0:8184:localhost:8184 ryko212@10.5.9.9 &
autossh -M 0 -i level5.key -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -L 8998:10.141.167.93:443 ryko212@10.5.9.9 &
autossh -M 0 -i level5.key -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -D 9555 ryko212@10.5.9.9 &
