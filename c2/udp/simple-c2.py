#!/usr/bin/python

import fcntl, os, select, socket, sys, time
from itertools import cycle, izip

UDP_IP = "0.0.0.0"
UDP_PORT = 58800
NUM_SOCKS = 32

key = "blarknob"

def crypt(m):
    return ''.join(chr(ord(c)^ord(k)) for c, k in izip(m, cycle(key)))

socks = {}

def main():
    print "Starting..."
    print "Waiting for connection."
    orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

    for i in range(0, NUM_SOCKS):
        socks[i].sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socks[i].sock.bind((UDP_IP, UDP_PORT + i))
        socks[i].addr = None
        socks[i].connected = False
        socks[i].lastconnect = time.time()

    while True:
        if select.select([sys.stdin], [], [], 0.0)[0]:
            data = sys.stdin.read().strip()
            if addr:
                sock.sendto(crypt(data) + '\n', addr)

        for i in range(0, NUM_SOCKS):
            if socks[i].connected and time.time() - socks[i].lastconnect > 20:
                print "Connection lost?"
                socks[i].connected = False

        if select.select([sock], [], [], 0.0)[0]:
            data, addr = sock.recvfrom(65535)
            if not connected:
                print "Connection from:", addr
                connected = True
            lastconnect = time.time()
            connected = True
            resp = crypt(data).replace("<<CRLCHK>>","")
            if len(resp) > 0:
                print resp
        time.sleep(0.5)

if __name__ == "__main__":
    main()
