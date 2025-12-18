@echo off
echo AIGC Pipeline Setup Assistant
echo ==============================
echo.

if exist ".env" (
    echo [INFO] .env file already exists.
    echo.
    echo Current configuration:
    type .env
    echo.
    set /p choice="Do you want to edit it? (y/n): "
    if /i "%choice%"=="y" (
        notepad .env
    )
) else (
    echo [INFO] Creating .env file from template...
    if exist ".env.example" (
        copy .env.example .env
        echo ✅ .env file created
        echo.
        echo Please edit .env file and add your API keys
        timeout /t 3 /nobreak >nul
        notepad .env
    ) else (
        echo [ERROR] .env.example template not found!
    )
)

echo.
echo Setup complete! Run run.bat to start the pipeline.
pause
