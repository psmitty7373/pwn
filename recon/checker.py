#!/usr/bin/python

import json, requests, socket, time

target = "10.5.S.H"

url = "https://192.168.43.73/hooks/o4cykjxqqffmpe3x5udphaxq6o"

ports = [[19, 21, 80, 445, 3389], [22, 80, 445, 3000, 8000]]
hosts = {}
while True:
    for s in range(0,65):
        for h in range(0,2):
            for p in ports[h]:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)
                ip = target.replace('S', str(s)).replace('H', str(h))
                result = sock.connect_ex((target.replace('S', str(s)).replace('H', str(h)), p))
                if result == 0:
                    if ip + ':' + str(p) in hosts.keys():
                        if hosts[ip + ':' + str(p)] < time.time() - 60 * 10:
                            requests.post(url, data=json.dumps({"text": "@channel " + ip + ":" + str(p) + " is BACK up!"}), verify=False)
                            hosts[ip + ':' + str(p)] = time.time()
                    else:
                        hosts[ip + ':' + str(p)] = time.time()
                        requests.post(url, data=json.dumps({"text": "@channel " + ip + ":" + str(p) + " is up!"}), verify=False)
