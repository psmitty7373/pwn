#!/bin/bash
autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -R 0.0.0.0:8184:localhost:8184 smitty@10.5.9.9
