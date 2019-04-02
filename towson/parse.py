#!/usr/bin/python

f = open('systems.txt','r').readlines()

l = {}
for i in range(1,6):
    l['l' + str(i)] = open(str(i) + 'linux.txt','w')
    l['w' + str(i)] = open(str(i) + 'win.txt','w')

print l

for q in f:
    q = q.strip().split(',')
    if 'inux' in q[5]:
        l['l' + q[0]].write(q[1] + '\n')
    else:
        l['w' + q[0]].write(q[1] + '\n')
