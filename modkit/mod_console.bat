@echo off
rem ====================================================================
rem  Savage Wind MOD console
rem
rem  All Chinese text is printed by modtool.py, never by this .bat.
rem  cmd reads .bat files in the system ANSI code page (CP936 here), so
rem  Chinese inside the script turns into mojibake on some machines.
rem  Keeping the control flow pure ASCII sidesteps that entirely.
rem ====================================================================
chcp 936 >nul 2>&1
setlocal enabledelayedexpansion
title Savage Wind MOD Console

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"
set "PYTOOL=%ROOT%\_tools\modtool.py"
set "INI=%ROOT%\mods_config.ini"
set "STAGE=%ROOT%\_enabled"

rem ---- locate python: never name a specific user's install path ----
set "PY="
for /f "delims=" %%i in ('where python 2^>nul') do if not defined PY set "PY=%%i"
if not defined PY for /f "delims=" %%i in ('where py 2^>nul') do if not defined PY set "PY=%%i -3"
if not defined PY if exist "%ROOT%\_tools\python\python.exe" set "PY=%ROOT%\_tools\python\python.exe"

if not defined PY (
  echo.
  echo   [!] Python not found. The console cannot run.
  echo.
  echo       Option 1: double-click launch_game.bat - it uses every group.
  echo       Option 2: install Python 3, then come back here.
  echo.
  pause
  exit /b 1
)

if not exist "%INI%" "%PY%" "%PYTOOL%" init >nul 2>&1

set "EMPTY=0"

:MAIN
cls
"%PY%" "%PYTOOL%" screen
set "CH="
set /p "CH="

if not defined CH goto BLANK
set "EMPTY=0"
if /i "%CH%"=="Q" goto END
if /i "%CH%"=="A" ( "%PY%" "%PYTOOL%" setall 1 & ping -n 2 127.0.0.1 >nul & goto MAIN )
if /i "%CH%"=="N" ( "%PY%" "%PYTOOL%" setall 0 & ping -n 2 127.0.0.1 >nul & goto MAIN )
if /i "%CH%"=="E" ( start notepad "%INI%" & goto MAIN )
if /i "%CH%"=="S" goto LAUNCH

rem  toggle exits 1 when no such group exists, so this needs no parsing.
"%PY%" "%PYTOOL%" toggle "%CH%" >nul 2>&1
ping -n 2 127.0.0.1 >nul
goto MAIN

:BLANK
set /a EMPTY+=1
if !EMPTY! geq 8 goto END
goto MAIN

rem ====================================================================
:LAUNCH
cls
"%PY%" "%PYTOOL%" build
if errorlevel 1 (
  echo.
  echo   [!] build failed.
  pause
  goto MAIN
)
"%PY%" "%PYTOOL%" status
"%PY%" "%PYTOOL%" msg launching
ping -n 4 127.0.0.1 >nul

rem ---- find the game: SAVAGEWIND_HOME wins, else probe next to this folder ----
set "GAME="
if defined SAVAGEWIND_HOME if exist "%SAVAGEWIND_HOME%\savagewind.exe" set "GAME=%SAVAGEWIND_HOME%"
if defined SAVAGEWIND_HOME if exist "%SAVAGEWIND_HOME%\build\savagewind.exe" set "GAME=%SAVAGEWIND_HOME%"
if not defined GAME if exist "%ROOT%\..\savagewind.exe" set "GAME=%ROOT%\.."
if not defined GAME if exist "%ROOT%\..\build\savagewind.exe" set "GAME=%ROOT%\.."

if not defined GAME (
  echo.
  echo   [!] savagewind.exe not found.
  echo.
  echo       Set SAVAGEWIND_HOME to the folder holding it, for example:
  echo           set SAVAGEWIND_HOME=D:\Games\SavageWind
  echo.
  pause
  goto MAIN
)

set "SAVAGEWIND_ROMFS_OVERLAY=%STAGE%"
rem  hud_letters_patch rewrites Bootup.pack and registers its growth in the
rem  ResourceSizeTable; when an overlay replaces that table the registry is
rem  skipped and the game crashes (c0000005). Turning the HUD letters off is
rem  what lets a mod overlay and the HUD patch coexist at all.
set "SAVAGEWIND_NO_HUD_LETTERS=1"

cd /d "%GAME%"
if exist "build\savagewind.exe" (
  build\savagewind.exe --play
) else (
  savagewind.exe --play
)

:AFTER
"%PY%" "%PYTOOL%" msg game_exit
pause
goto MAIN

:END
endlocal
exit /b 0
