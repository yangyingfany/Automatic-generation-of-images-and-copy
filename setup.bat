@echo off
chcp 65001 >nul
title AIGC Setup Helper
color 0B

echo.
echo ================================================
echo        AIGC Pipeline Setup Helper
echo ================================================
echo.

echo This will help you configure the API keys.
echo.
echo Current API keys in main.py are DEFAULT keys.
echo You need to replace them with your own.
echo.
echo Required API keys:
echo 1. Coze Bot ID and API Key
echo    Get from: https://www.coze.cn/open
echo 2. DeepSeek API Key
echo    Get from: https://platform.deepseek.com
echo.

set /p action="Open main.py for editing now? (y/n): "
if /i "%action%"=="y" (
    echo Opening main.py in Notepad...
    notepad main.py
    echo.
    echo After editing, save the file and run run.bat
    pause
    exit /b 0
)

echo.
echo You can also:
echo 1. Manually edit main.py with any text editor
echo 2. Look for COZE_CONFIG and DEEPSEEK_API_KEY
echo 3. Replace the values with your own keys
echo 4. Save and run run.bat
echo.
pause
