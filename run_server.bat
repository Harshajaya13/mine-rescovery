@echo off
TITLE Mine Rescue Rover — Mission Control Server
COLOR 0A

echo ===================================================
echo   Starting Mine Rescue Rover Mission Control
echo ===================================================
echo.

:: 1. Navigate to laptop_server directory
if exist "C:\Users\Kesava\Desktop\mine_rescue_rover\laptop_server" (
    cd /d "C:\Users\Kesava\Desktop\mine_rescue_rover\laptop_server"
) else (
    cd /d "%~dp0"
    if exist "laptop_server" (
        cd laptop_server
    )
)

echo [INFO] Working Directory: %CD%

:: 2. Launch dashboard in default browser
echo [INFO] Launching Mission Control UI at http://localhost:5000 ...
start http://localhost:5000

:: 3. Find Python Executable (Prefers venv directly to avoid batch exit bugs)
set "PY_CMD=python"

if exist "venv\Scripts\python.exe" (
    echo [INFO] Found venv: venv\Scripts\python.exe
    set "PY_CMD=venv\Scripts\python.exe"
) else if exist "..\venv\Scripts\python.exe" (
    echo [INFO] Found venv: ..\venv\Scripts\python.exe
    set "PY_CMD=..\venv\Scripts\python.exe"
) else if exist "C:\Users\Kesava\Desktop\mine_rescue_rover\venv\Scripts\python.exe" (
    echo [INFO] Found venv: C:\Users\Kesava\Desktop\mine_rescue_rover\venv\Scripts\python.exe
    set "PY_CMD=C:\Users\Kesava\Desktop\mine_rescue_rover\venv\Scripts\python.exe"
) else (
    echo [WARNING] venv not found. Using system Python...
)

echo.
echo [INFO] Executing: %PY_CMD% server.py
echo ===================================================
echo.

:: 4. Run server.py
"%PY_CMD%" server.py

echo.
echo ===================================================
echo Server stopped or exited. Window will stay open.
echo ===================================================
pause
