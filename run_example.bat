@echo off
chcp 65001 >nul
title 🎨 AIGC内容生成流水线
color 0A

echo.
echo ================================================
echo        🚀 AIGC三合一内容生成系统
echo ================================================
echo.

echo [1] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python
    echo 请先安装Python 3.8或更高版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [2] 检查依赖包...
pip show requests >nul 2>&1
if errorlevel 1 (
    echo ⚠️  正在安装requests库...
    pip install requests --quiet
    echo ✅ requests库安装完成
) else (
    echo ✅ requests库已安装
)

echo [3] 检查配置文件...
if not exist ".env" (
    echo ⚠️  未找到配置文件 .env
    echo 正在从模板创建配置文件...
    
    if exist ".env.example" (
        copy .env.example .env >nul
        echo ✅ 已创建 .env 文件
        echo.
        echo ⚠️ 重要提示：
        echo 请打开 .env 文件，填写你的API密钥：
        echo 1. COZE_BOT_ID 和 COZE_API_KEY
        echo 2. DEEPSEEK_API_KEY
        echo.
        echo 配置完成后重新运行此脚本
    ) else (
        echo ❌ 错误：找不到 .env.example 模板文件
    )
    pause
    exit /b 1
)

echo [4] 检查ComfyUI服务...
timeout /t 2 /nobreak >nul

echo [5] 启动生成流水线...
echo ================================================
echo.

python main.py

echo.
echo ================================================
echo 生成完成！图片保存在 comfyui_outputs 文件夹
echo ================================================
pause
