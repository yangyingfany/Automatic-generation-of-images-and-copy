@echo off
title AIGC Pipeline
color 0A

echo.
echo ================================================
echo        AIGC Content Generation System
echo ================================================
echo.

echo [INFO] Checking Python installation...
python --version 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found or not in PATH
    echo Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)

echo [INFO] Checking requests library...
pip show requests >nul 2>nul
if errorlevel 1 (
    echo [INFO] Installing requests library...
    pip install requests --quiet
    echo [OK] requests installed
) else (
    echo [OK] requests already installed
)

echo [INFO] Checking output directory...
if not exist "comfyui_outputs" (
    mkdir comfyui_outputs
    echo [OK] Created comfyui_outputs folder
) else (
    echo [OK] Output folder exists
)

echo.
echo ================================================
echo [INFO] Starting generation...
echo [NOTE] Using API keys from main.py code
echo [NOTE] To change keys, edit main.py file
echo ================================================
echo.

python main.py

echo.
echo ================================================
echo [INFO] Process completed
echo [INFO] Check comfyui_outputs folder for images
echo ================================================
echo.
pause
