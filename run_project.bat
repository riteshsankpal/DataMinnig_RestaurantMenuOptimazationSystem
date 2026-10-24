@echo off
setlocal EnableDelayedExpansion
rem ---------------------------------------------------------------
rem  Restaurant Menu Optimization System - one-click launcher (Windows)
rem  Works from any folder because it first moves to its own location.
rem ---------------------------------------------------------------
cd /d "%~dp0"
title Restaurant Menu Optimization System
echo.
echo  Restaurant Menu Optimization System
echo  ===================================
echo.

rem --- 1. find Python (3.9 or newer) ---
set "PY="
py -3 -c "import sys; sys.exit(0 if sys.version_info>=(3,9) else 1)" >nul 2>nul && set "PY=py -3"
if not defined PY (
    python -c "import sys; sys.exit(0 if sys.version_info>=(3,9) else 1)" >nul 2>nul && set "PY=python"
)
if not defined PY (
    echo  [ERROR] Python 3.9 or newer was not found.
    echo.
    echo  1. Download Python from https://www.python.org/downloads/
    echo  2. During installation, tick "Add python.exe to PATH".
    echo  3. Close this window and double-click run_project.bat again.
    echo.
    pause
    exit /b 1
)
echo  Using Python: %PY%

rem --- 2. create the virtual environment once ---
if not exist ".venv\Scripts\python.exe" (
    echo  Creating virtual environment in .venv ...
    %PY% -m venv .venv
    if errorlevel 1 (
        echo  [ERROR] Could not create the virtual environment.
        pause
        exit /b 1
    )
)

rem --- 3. install dependencies once (needs internet the first time) ---
if not exist ".venv\.deps_ok" (
    echo  Installing dependencies. This can take a few minutes the first time ...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>nul
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo  [WARNING] Full install failed. Trying again without MLxtend.
        echo  The app will use its built-in Apriori instead, with the same results.
        ".venv\Scripts\python.exe" -m pip install -r requirements-core.txt
        if errorlevel 1 (
            echo  [ERROR] Dependency installation failed. Check your internet connection and read the Troubleshooting section of README.md.
            pause
            exit /b 1
        )
    )
    echo ok> ".venv\.deps_ok"
)

rem --- 4. make sure the data files exist ---
if not exist "data\orders.csv" (
    echo  Data files not found. Generating the synthetic demo data ...
    ".venv\Scripts\python.exe" tools\generate_data.py
)

rem --- 5. open the browser a few seconds after the server starts, then run Flask ---
echo.
echo  Starting the server. Keep this window open while you use the site.
echo  Website: http://127.0.0.1:5000     (press Ctrl+C here to stop)
echo.
start "" cmd /c "timeout /t 4 /nobreak >nul & start http://127.0.0.1:5000"
".venv\Scripts\python.exe" app.py
if errorlevel 1 (
    echo.
    echo  [ERROR] The server stopped with an error. Read the message above.
)
pause
