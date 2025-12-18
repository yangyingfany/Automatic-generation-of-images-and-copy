@echo off
chcp 65001 >nul
title AIGC Pipeline
color 0A

echo.
echo ================================================
echo        AIGC Content Generation System
echo ================================================
echo.

echo [INFO] Loading configuration from .env file...
echo.

:: 检查.env文件是否存在
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo.
    echo Please:
    echo 1. Copy .env.example to .env
    echo 2. Edit .env and add your API keys
    echo 3. Run again
    echo.
    pause
    exit /b 1
)

:: 加载.env文件中的变量
for /f "usebackq tokens=*" %%i in (".env") do (
    for /f "tokens=1,2 delims==" %%a in ("%%i") do (
        if not "%%a"=="" if not "%%b"=="" (
            set "%%a=%%b"
        )
    )
)

:: 显示加载的配置（隐藏敏感信息）
echo [CONFIG] Coze Bot ID: %COZE_BOT_ID%
echo [CONFIG] Coze API Key: %COZE_API_KEY:~0,10%...
echo [CONFIG] DeepSeek API Key: %DEEPSEEK_API_KEY:~0,10%...
echo.

echo [INFO] Checking Python...
python --version
if errorlevel 1 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

echo [INFO] Checking dependencies...
pip show requests >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing requests...
    pip install requests --quiet
)

echo [INFO] Creating output directory...
if not exist "comfyui_outputs" mkdir comfyui_outputs

echo.
echo ================================================
echo [INFO] Starting generation...
echo ================================================
echo.

:: 设置环境变量并运行Python
set COZE_BOT_ID=%COZE_BOT_ID%
set COZE_API_KEY=%COZE_API_KEY%
set DEEPSEEK_API_KEY=%DEEPSEEK_API_KEY%

python main.py

echo.
echo ================================================
echo [INFO] Process completed!
echo ================================================
pause
