#!/usr/bin/python

import fcntl, os, select, socket, sys, time
from itertools import cycle, izip

UDP_IP = "0.0.0.0"
UDP_PORT = 8888

key = "blarknob"

def crypt(m):
    return ''.join(chr(ord(c)^ord(k)) for c, k in izip(m, cycle(key)))

def main():
    print "Starting..."
    print "Waiting for connection."
    orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    addr = None
    connected = False
    lastconnect = time.time()

    while True:
        if connected and time.time() - lastconnect > 20:
            print "Connection lost?"
            connected = False
        if select.select([sys.stdin], [], [], 0.0)[0]:
            data = sys.stdin.read().strip()
            if addr:
                sock.sendto(crypt(data) + '\n', addr)
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
