# AIGC三合一生成流水线

一个整合Coze、DeepSeek和ComfyUI的自动化内容生成系统，输入一个想法，自动输出营销文案+优化提示词+图片。

## 🎯 项目简介

本项目实现了端到端的AIGC内容生成流水线：
1. **文案生成** - 使用Coze API生成中文营销文案
2. **提示词优化** - 使用DeepSeek API转换为SD专业提示词
3. **图片生成** - 使用ComfyUI生成图片

## 🚀 快速开始

### 环境要求
- Python 3.8+
- ComfyUI 本地运行（默认端口8188）
- Coze API 密钥
- DeepSeek API 密钥

### 安装步骤
```bash
# 1. 克隆仓库
git clone https://github.com/你的用户名/仓库名.git
cd 仓库名

# 2. 安装依赖
pip install requests

# 3. 配置API密钥
复制 .env.example 为 .env 并填写你的密钥
