@echo off
chcp 65001 >nul
title AIGC Pipeline
color 0A

echo.
echo ================================================
echo        AIGC Content Generation System
echo ================================================
echo.

echo [1] Checking Python installation...
python --version 2>nul
if errorlevel 1 (
    echo ERROR: Python not found or not in PATH
    echo.
    echo Please install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [2] Checking dependencies...
pip show requests >nul 2>nul
if errorlevel 1 (
    echo Installing requests library...
    pip install requests --quiet
    echo OK: requests installed
) else (
    echo OK: requests already installed
)

echo [3] Checking configuration...
echo IMPORTANT: Make sure you have edited main.py
echo and replaced the API keys with your own.
echo.
echo Current API keys in main.py:
echo Coze Bot ID: 7584493784956796974
echo Coze API Key: pat_ivmwvr7EwaQbUb9ZqonpvZYjXLpjTOi1Dt9w5kwehdbI66Bxh06344to4U6QsjGz
echo DeepSeek API Key: sk-7b64922f9d6848f99f53204229c9cddb
echo.
set /p confirm="Are these your API keys? (y/n): "
if /i "%confirm%" neq "y" (
    echo.
    echo Please edit main.py file to change API keys.
    echo Open main.py in Notepad? (y/n):
    set /p edit=
    if /i "%edit%"=="y" notepad main.py
    echo Please restart after editing.
    pause
    exit /b 1
)

echo [4] Creating output directory...
if not exist "comfyui_outputs" (
    mkdir comfyui_outputs
    echo Created output directory
) else (
    echo Output directory exists
)

echo.
echo ================================================
echo Starting generation...
echo Topic: "A Gundam model"
echo ================================================
echo.

python main.py

echo.
echo ================================================
echo Process completed!
echo ================================================
pause
