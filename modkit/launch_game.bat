@echo off
rem ====================================================================
rem  Launch Savage Wind with every MOD group on, no console UI.
rem  Pure ASCII control flow; Chinese comes from modtool.py.
rem ====================================================================
chcp 936 >nul 2>&1
setlocal
title Savage Wind

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"
set "PYTOOL=%ROOT%\_tools\modtool.py"
set "STAGE=%ROOT%\_enabled"

set "PY="
for /f "delims=" %%i in ('where python 2^>nul') do if not defined PY set "PY=%%i"
if not defined PY for /f "delims=" %%i in ('where py 2^>nul') do if not defined PY set "PY=%%i -3"

if not defined PY goto NO_PY

rem  Build with the settings already in mods_config.ini. This is not
rem  "force everything on": honouring the ini is the whole point.
"%PY%" "%PYTOOL%" build
if errorlevel 1 (
  echo.
  echo   [!] build failed.
  pause
  exit /b 1
)

set "GAME="
if defined SAVAGEWIND_HOME if exist "%SAVAGEWIND_HOME%\savagewind.exe" set "GAME=%SAVAGEWIND_HOME%"
if defined SAVAGEWIND_HOME if exist "%SAVAGEWIND_HOME%\build\savagewind.exe" set "GAME=%SAVAGEWIND_HOME%"
if not defined GAME if exist "%ROOT%\..\savagewind.exe" set "GAME=%ROOT%\.."
if not defined GAME if exist "%ROOT%\..\build\savagewind.exe" set "GAME=%ROOT%\.."

if not defined GAME goto NO_GAME
if not exist "%STAGE%" goto NO_STAGE

set "SAVAGEWIND_ROMFS_OVERLAY=%STAGE%"
set "SAVAGEWIND_NO_HUD_LETTERS=1"

cd /d "%GAME%"
if exist "build\savagewind.exe" (
  build\savagewind.exe --play
) else (
  savagewind.exe --play
)
if errorlevel 1 (
  echo.
  echo   [!] the game exited with code %errorlevel%.
  pause
)
endlocal
exit /b 0

:NO_PY
echo.
echo   [!] Python not found, cannot build the overlay folder.
echo       Install Python 3, or build it once with mod_console.bat.
echo.
pause
endlocal
exit /b 1

:NO_STAGE
echo.
echo   [!] the overlay folder was not produced: %STAGE%
echo.
pause
endlocal
exit /b 1

:NO_GAME
echo.
echo   [!] savagewind.exe not found.
echo       Set SAVAGEWIND_HOME to the folder that holds it.
echo.
pause
endlocal
exit /b 1
