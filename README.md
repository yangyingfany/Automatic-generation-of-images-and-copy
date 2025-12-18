# 🎨 AIGC内容生成流水线 - 使用指南

## 📋 项目简介

这是一个全自动的AIGC内容生成系统，将三个AI服务串联起来：
1. **文案创作**：使用Coze API生成中文营销文案
2. **提示词优化**：使用DeepSeek API转换为专业绘画提示词
3. **图像生成**：使用ComfyUI生成图片

**输入一个想法 → 自动生成完整的营销内容包（文案+提示词+图片）**

## ⚙️ 配置步骤（重要！）

在运行程序前，必须先配置API密钥：

步骤1：编辑主程序文件

用文本编辑器打开 main.py，找到配置部分：
#========== 用户配置区 ==========
COZE_CONFIG = {
    "bot_id": "7584493784956796974",  # ← 替换为你的Coze Bot ID
    "api_key": "pat_ivmwvr7EwaQbUb9ZqonpvZYjXLpjTOi1Dt9w5kwehdbI66Bxh06344to4U6QsjGz"  # ← 替换为你的Coze API密钥
}
DEEPSEEK_API_KEY = "sk-7b64922f9d6848f99f53204229c9cddb"  # ← 替换为你的DeepSeek API密钥

步骤2：获取API密钥

# Coze API密钥获取：
# 访问 https://www.coze.cn/open
# 注册/登录 → 工作台 → 获取 Bot ID 和 API Key
# DeepSeek API密钥获取：
# 访问 https://platform.deepseek.com/
# 注册/登录 → API管理 → 创建API密钥

步骤3：填写并保存
# 编辑保存后运行
python main.py

## 🛠️ 环境要求
软件要求：
bash
# Python 3.8+（必须安装并添加到系统PATH）
# 下载地址：https://www.python.org/downloads/

# ComfyUI（本地运行，用于图像生成）
# 下载地址：https://github.com/comfyanonymous/ComfyUI

安装Python依赖：
bash
pip install requests
🖼️ ComfyUI配置
本地运行ComfyUI：
bash
# 1. 下载安装ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI

# 2. 下载模型文件（保存到指定目录）
# 模型名称：anything-v5-PrtRE.safetensors
# 保存路径：ComfyUI/models/checkpoints/

# 3. 启动ComfyUI
python main.py

# 4. 验证服务运行
# 浏览器访问：http://127.0.0.1:8188


## 📝 使用方法

运行程序：
bash
# 方式1：Windows双击运行
双击 run_simple.bat

# 方式2：命令行运行
python main.py

修改生成主题：
编辑 main.py 文件最后部分：

python
if __name__ == "__main__":
    USER_TOPIC = "你想要的主题"  # 修改这里
    # 例如：
    # USER_TOPIC = "夏日海滩度假场景"
    # USER_TOPIC = "未来科技城市夜景"
    # USER_TOPIC = "可爱猫咪玩毛线球"


## 📊 输出结果

程序运行成功后，输出文件结构：

text
comfyui_outputs/
├── comfy_1700000000_a1b2c3.png
├── comfy_1700000001_d4e5f6.png
└── ...
控制台输出内容：

bash
========================================
启动AIGC生成流水线
========================================

🔄 步骤1: 生成文案...
✅ 文案生成成功: 全新限量版高达模型...

🔄 步骤2: 优化提示词...
✅ 提示词优化成功: (masterpiece, best quality...

🔄 步骤3: 准备ComfyUI工作流...
✅ 工作流构建完成

🔄 步骤4: 生成图片...
✅ 图片生成完成
💾 图片已保存: comfyui_outputs/comfy_1700000000_a1b2c3.png
















