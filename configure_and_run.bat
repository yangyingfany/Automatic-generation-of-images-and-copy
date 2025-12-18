@echo off
chcp 65001 >nul
title AIGC Configuration
color 0A

echo.
echo ================================================
echo        AIGC System Configuration
echo ================================================
echo.

:config_menu
echo [1] Use default API keys (from code)
echo [2] Enter your own API keys
echo [3] Run without configuration
echo.
set /p choice="Choose option (1/2/3): "

if "%choice%"=="1" goto run_default
if "%choice%"=="2" goto custom_config
if "%choice%"=="3" goto run_direct
goto config_menu

:custom_config
echo.
echo Please enter your API keys:
echo.
set /p COZE_BOT_ID="Coze Bot ID (press Enter to skip): "
set /p COZE_API_KEY="Coze API Key (press Enter to skip): "
set /p DEEPSEEK_API_KEY="DeepSeek API Key (press Enter to skip): "
set /p COMFYUI_SERVER_URL="ComfyUI URL [default: http://127.0.0.1:8188]: "

:: 如果用户输入了值，设置环境变量
if not "%COZE_BOT_ID%"=="" set COZE_BOT_ID=%COZE_BOT_ID%
if not "%COZE_API_KEY%"=="" set COZE_API_KEY=%COZE_API_KEY%
if not "%DEEPSEEK_API_KEY%"=="" set DEEPSEEK_API_KEY=%DEEPSEEK_API_KEY%
if not "%COMFYUI_SERVER_URL%"=="" set COMFYUI_SERVER_URL=%COMFYUI_SERVER_URL%

goto run_program

:run_default
echo.
echo Using default API keys from code...
:: 不设置环境变量，让Python使用代码中的默认值
goto run_program

:run_direct
echo.
echo Running with current configuration...
goto run_program

:run_program
echo.
echo ================================================
echo Starting AIGC Pipeline...
echo ================================================
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

:: 检查依赖
pip show requests >nul 2>&1
if errorlevel 1 (
    echo Installing requests...
    pip install requests --quiet
)

:: 创建输出目录
if not exist "comfyui_outputs" mkdir comfyui_outputs

:: 运行主程序
python main.py

echo.
echo ================================================
echo Generation complete!
echo ================================================
pause
