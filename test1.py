import requests
import json
import time
import os
import shutil
from PIL import Image, ImageDraw, ImageFont

# ========== 用户配置区 ==========
COZE_CONFIG = {
    "bot_id": "7584493784956796974",
    "api_key": "pat_ivmwvr7EwaQbUb9ZqonpvZYjXLpjTOi1Dt9w5kwehdbI66Bxh06344to4U6QsjGz"
}
DEEPSEEK_API_KEY = "sk-7b64922f9d6848f99f53204229c9cddb"
COMFYUI_CONFIG = {
    "server_url": "http://127.0.0.1:8188",
    "workflow_file": "test1.json",
    "positive_node_id": "1",
    "output_base_dir": "./comfyui_outputs"  # 改为基础目录
}


# ========== 获取下一个可用输出目录 ==========
def get_next_output_dir(base_dir):
    """获取下一个可用的输出目录，如 output1, output2, ..."""
    # 确保基础目录存在
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # 查找已存在的输出目录
    existing_dirs = []
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path) and item.startswith("output"):
            try:
                # 提取数字部分
                dir_num = int(item.replace("output", ""))
                existing_dirs.append(dir_num)
            except ValueError:
                continue

    # 确定下一个数字
    next_num = 1
    if existing_dirs:
        next_num = max(existing_dirs) + 1

    output_dir = os.path.join(base_dir, f"output{next_num}")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    print(f"📁 创建输出目录: {output_dir}")
    return output_dir


# ========== Coze文案生成（修改版）==========
def generate_copywriting_with_coze(prompt, bot_id, api_key):
    """生成营销文案，返回文案内容和聊天记录"""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    chat_url = "https://api.coze.cn/v3/chat"

    # 优化提示词，要求生成详细的营销文案
    enhanced_prompt = f"""请创作一则关于"{prompt}"的营销文案。
要求：
1. 包含吸引人的标题（20字以内）
2. 产品卖点描述（3-5个要点）
3. 品牌口号或标语
4. 呼吁行动语句
5. 整体字数控制在150-200字之间

请以清晰的段落格式输出。"""

    chat_data = {
        "bot_id": bot_id,
        "user_id": "user_123456",
        "stream": False,
        "auto_save_history": True,
        "additional_messages": [{"role": "user", "content": enhanced_prompt, "content_type": "text"}]
    }

    try:
        print("🔄 正在生成文案...")
        resp = requests.post(chat_url, headers=headers, json=chat_data, timeout=30)
        chat_result = resp.json()

        if chat_result.get("code") != 0:
            print(f"❌ Coze对话失败: {chat_result.get('msg')}")
            return None, None

        chat_id = chat_result["data"]["id"]
        conversation_id = chat_result["data"]["conversation_id"]

        # 轮询对话状态
        retrieve_url = "https://api.coze.cn/v3/chat/retrieve"
        for i in range(30):
            time.sleep(1)
            params = {"chat_id": chat_id, "conversation_id": conversation_id}
            resp = requests.get(retrieve_url, headers=headers, params=params, timeout=30)
            status_result = resp.json()
            if status_result.get("code") == 0 and status_result["data"]["status"] == "completed":
                break

        # 获取完整的对话历史
        list_msg_url = "https://api.coze.cn/v3/chat/message/list"
        params = {"chat_id": chat_id, "conversation_id": conversation_id}
        resp = requests.get(list_msg_url, headers=headers, params=params, timeout=30)
        msg_result = resp.json()

        copywriting = None
        conversation_text = ""

        if msg_result.get("code") == 0:
            for msg in msg_result.get("data", []):
                role = msg.get("role", "")
                content = msg.get("content", "").strip()

                if role == "user":
                    conversation_text += f"用户: {content}\n\n"
                elif role == "assistant" and msg.get("type") == "answer":
                    conversation_text += f"AI助手: {content}\n\n"
                    if not copywriting:  # 只取第一个AI回复作为文案
                        copywriting = content

        print("✅ 文案生成成功")
        return copywriting, conversation_text

    except Exception as e:
        print(f"❌ Coze API错误: {e}")
        return None, None


# ========== DeepSeek提示词优化 ==========
def optimize_prompt_with_deepseek(original_text, api_key):
    """将中文文案优化为Stable Diffusion提示词"""
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    system_prompt = """你是一个专业的Stable Diffusion提示词工程师。请将用户输入的中文营销文案，优化为适合文生图模型的、高质量英文提示词。
    输出必须是纯英文，采用标准格式：(masterpiece, best quality, ultra detailed), [主体描述], [环境与光照], [艺术风格], [色彩氛围]。
    添加质量标签：masterpiece, best quality, ultra detailed, 8k, realistic。
    只返回优化后的提示词，不要任何解释。"""

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": original_text}
        ],
        "stream": False,
        "max_tokens": 500
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        result = response.json()
        optimized_prompt = result["choices"][0]["message"]["content"].strip()
        # 清理输出
        cleaned_prompt = optimized_prompt.replace('```', '').replace('prompt:', '').replace('Prompt:', '').strip()
        return cleaned_prompt
    except Exception as e:
        print(f"❌ DeepSeek API错误: {e}")
        return None


# ========== 简化的工作流转换 ==========
def load_and_customize_workflow(workflow_file, positive_prompt, node_id):
    """加载并自定义ComfyUI工作流"""
    try:
        print("📋 构建工作流...")

        # 基于你的JSON文件硬编码工作流
        api_prompt = {
            "1": {  # CLIPTextEncode (正向)
                "class_type": "CLIPTextEncode",
                "inputs": {"text": positive_prompt, "clip": ["4", 1]}
            },
            "2": {  # KSampler
                "class_type": "KSampler",
                "inputs": {
                    "seed": 737705583854619,
                    "steps": 20,
                    "cfg": 8,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["1", 0],
                    "negative": ["5", 0],
                    "latent_image": ["7", 0]
                }
            },
            "3": {  # VAEDecode
                "class_type": "VAEDecode",
                "inputs": {"samples": ["2", 0], "vae": ["4", 2]}
            },
            "4": {  # CheckpointLoaderSimple
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "anything-v5-PrtRE.safetensors"}
            },
            "5": {  # CLIPTextEncode (负向)
                "class_type": "CLIPTextEncode",
                "inputs": {"text": "", "clip": ["4", 1]}
            },
            "6": {  # SaveImage
                "class_type": "SaveImage",
                "inputs": {"filename_prefix": "ComfyUI", "images": ["3", 0]}
            },
            "7": {  # EmptyLatentImage
                "class_type": "EmptyLatentImage",
                "inputs": {"width": 512, "height": 512, "batch_size": 1}
            }
        }

        print(f"✅ 工作流构建完成")
        return api_prompt

    except Exception as e:
        print(f"❌ 工作流构建失败: {e}")
        import traceback
        traceback.print_exc()
        return None


# ========== ComfyUI 工作流触发 ==========
def trigger_comfyui_workflow(workflow_payload, server_url, output_dir):
    """触发ComfyUI工作流生成图片"""
    # 确保使用绝对路径
    output_dir = os.path.abspath(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 先测试连接
    try:
        test_resp = requests.get(f"{server_url}/system_stats", timeout=5)
        if test_resp.status_code != 200:
            print(f"❌ ComfyUI服务器不可用")
            return None
    except:
        print(f"❌ 无法连接到ComfyUI服务器")
        return None

    # 提交任务
    queue_url = f"{server_url}/prompt"
    try:
        print("🔄 提交任务至ComfyUI...")

        # 调试：打印前几个节点的配置
        for node_id, config in list(workflow_payload.items())[:3]:
            print(f"  节点 {node_id}: {config['class_type']}")

        resp = requests.post(queue_url, json={"prompt": workflow_payload}, timeout=30)

        if resp.status_code != 200:
            error_data = resp.json()
            print(f"❌ 提交失败:")
            print(f"   错误: {error_data.get('error', {}).get('message', '未知错误')}")

            # 打印节点错误
            if 'node_errors' in error_data:
                for node_id, errors in error_data['node_errors'].items():
                    print(f"   节点 {node_id} 错误: {errors.get('errors', [{}])[0].get('details', '未知')}")

            return None

        result = resp.json()
        prompt_id = result['prompt_id']
        print(f"✅ 任务提交成功，Prompt ID: {prompt_id}")

    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return None

    # 等待完成
    print("等待图片生成...")
    history_url = f"{server_url}/history"

    for i in range(60):
        time.sleep(2)
        try:
            history_resp = requests.get(history_url, timeout=10)
            history = history_resp.json()
            if prompt_id in history:
                print("✅ 图片生成完成")
                break
            if i % 10 == 0:
                print(f"  等待中... ({i * 2}秒)")
        except:
            continue

    if i == 59:
        print("❌ 图片生成超时")
        return None

    # 下载图片
    try:
        result_data = history[prompt_id]
        images_output = []

        for node_id, node_output in result_data['outputs'].items():
            if 'images' in node_output:
                for image in node_output['images']:
                    filename = image['filename']
                    subfolder = image.get('subfolder', '')

                    if subfolder:
                        image_url = f"{server_url}/view?filename={filename}&subfolder={subfolder}&type=output"
                    else:
                        image_url = f"{server_url}/view?filename={filename}&type=output"

                    image_resp = requests.get(image_url)
                    if image_resp.status_code == 200:
                        timestamp = int(time.time())
                        # 使用绝对路径保存图片
                        save_path = os.path.join(output_dir, f"comfy_{timestamp}_{prompt_id[:6]}.png")
                        with open(save_path, 'wb') as f:
                            f.write(image_resp.content)
                        images_output.append(save_path)
                        print(f"💾 图片已保存: {save_path}")

        return images_output if images_output else None

    except Exception as e:
        print(f"❌ 图片下载失败: {e}")
        return None


# ========== 创建图文整合文件 ==========
def create_image_with_text(image_path, copywriting, output_dir, user_topic):
    """将图片和文案整合到一个文件中"""
    try:
        # 确保使用绝对路径
        image_path = os.path.abspath(image_path)
        output_dir = os.path.abspath(output_dir)

        # 读取图片
        img = Image.open(image_path)
        img_width, img_height = img.size

        # 创建新图片，高度增加用于放置文案
        text_height = 400  # 文案区域高度
        new_img = Image.new('RGB', (img_width, img_height + text_height), color='white')

        # 粘贴原图片
        new_img.paste(img, (0, 0))

        # 添加文案区域
        draw = ImageDraw.Draw(new_img)

        # 设置字体（使用系统字体）
        try:
            font_title = ImageFont.truetype("simhei.ttf", 24)  # 黑体
            font_text = ImageFont.truetype("simsun.ttc", 16)  # 宋体
        except:
            # 如果找不到字体，使用默认字体
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()

        # 绘制标题区域
        draw.rectangle([(0, img_height), (img_width, img_height + 50)], fill='#f0f0f0')
        draw.text((20, img_height + 15), "📝 营销文案", fill='#333333', font=font_title)

        # 绘制分隔线
        draw.line([(0, img_height + 50), (img_width, img_height + 50)], fill='#cccccc', width=1)

        # 绘制文案内容
        y_position = img_height + 70
        x_margin = 20

        # 分割文案为多行
        lines = []
        current_line = ""

        for char in copywriting:
            if char == '\n':
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                lines.append("")  # 空行
            else:
                current_line += char
                # 每行约45个字符
                if len(current_line) >= 45 and char in ['，', '。', '！', '？', '；', '、', ' ', '.', ',']:
                    lines.append(current_line)
                    current_line = ""

        if current_line:
            lines.append(current_line)

        # 绘制每一行
        for line in lines[:15]:  # 最多显示15行
            if y_position < img_height + text_height - 20:
                draw.text((x_margin, y_position), line, fill='#333333', font=font_text)
                y_position += 25

        # 如果文案太长，添加提示
        if len(lines) > 15:
            draw.text((x_margin, img_height + text_height - 30),
                      f"...（文案过长，已截断部分内容）",
                      fill='#666666', font=font_text)

        # 保存整合后的图片
        timestamp = int(time.time())
        base_name = os.path.basename(image_path).split('.')[0]
        output_path = os.path.join(output_dir, f"final_output_{base_name}.png")

        new_img.save(output_path, 'PNG', quality=95)

        # 同时保存纯文本文件
        text_path = os.path.join(output_dir, f"copywriting_{base_name}.txt")
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write("=" * 50 + "\n")
            f.write(f"营销文案 - {user_topic}\n")
            f.write("=" * 50 + "\n\n")
            f.write(copywriting)
            f.write("\n\n" + "=" * 50 + "\n")
            f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"主题: {user_topic}\n")

        return output_path, text_path

    except Exception as e:
        print(f"❌ 创建图文文件失败: {e}")
        return image_path, None


# ========== 创建项目摘要文件 ==========
def create_project_summary(output_dir, user_topic, copywriting, sd_prompt, final_image_path):
    """创建项目摘要文件，包含所有生成信息"""
    try:
        summary_path = os.path.join(output_dir, "project_summary.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("AIGC项目生成摘要\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"📌 项目主题: {user_topic}\n")
            f.write(f"📅 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"📁 输出目录: {os.path.basename(output_dir)}\n\n")

            f.write("-" * 60 + "\n")
            f.write("📝 营销文案\n")
            f.write("-" * 60 + "\n")
            f.write(copywriting)
            f.write("\n\n")
            f.write(f"文案字数: {len(copywriting)}字\n\n")

            f.write("-" * 60 + "\n")
            f.write("🎨 Stable Diffusion提示词\n")
            f.write("-" * 60 + "\n")
            f.write(sd_prompt)
            f.write("\n\n")

            f.write("-" * 60 + "\n")
            f.write("🖼️  生成文件\n")
            f.write("-" * 60 + "\n")

            # 列出目录中所有文件
            for item in sorted(os.listdir(output_dir)):
                item_path = os.path.join(output_dir, item)
                if os.path.isfile(item_path):
                    size_kb = os.path.getsize(item_path) / 1024
                    f.write(f"  • {item} ({size_kb:.1f} KB)\n")

            f.write("\n" + "=" * 60 + "\n")
            f.write("生成流程完成\n")
            f.write("=" * 60 + "\n")

        print(f"📋 项目摘要已创建: {summary_path}")
        return summary_path
    except Exception as e:
        print(f"❌ 创建项目摘要失败: {e}")
        return None


# ========== 修改后的主流程 ==========
def main_pipeline(user_topic):
    print("=" * 60)
    print("启动AIGC生成流水线")
    print("=" * 60)

    # 1. 获取新的输出目录
    output_dir = get_next_output_dir(COMFYUI_CONFIG['output_base_dir'])

    # 2. 生成文案
    print("\n🔄 步骤1: 生成文案...")
    copywriting, conversation_text = generate_copywriting_with_coze(
        user_topic, COZE_CONFIG["bot_id"], COZE_CONFIG["api_key"]
    )

    if not copywriting:
        print("❌ 文案生成失败，流程终止")
        return

    print(f"✅ 文案生成成功:")
    print("-" * 40)
    print(copywriting[:200] + "..." if len(copywriting) > 200 else copywriting)
    print("-" * 40)

    # 保存完整对话记录
    if conversation_text:
        conv_path = os.path.join(output_dir, "conversation.txt")
        with open(conv_path, 'w', encoding='utf-8') as f:
            f.write(conversation_text)
        print(f"💾 对话记录已保存: {conv_path}")

    # 3. 优化提示词
    print("\n🔄 步骤2: 优化提示词...")
    sd_prompt = optimize_prompt_with_deepseek(copywriting, DEEPSEEK_API_KEY)
    if not sd_prompt:
        print("❌ 提示词优化失败，流程终止")
        return

    print(f"✅ 提示词优化成功:")
    print("-" * 40)
    print(sd_prompt[:100] + "..." if len(sd_prompt) > 100 else sd_prompt)
    print("-" * 40)

    # 保存提示词
    prompt_path = os.path.join(output_dir, "sd_prompt.txt")
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(sd_prompt)
    print(f"💾 提示词已保存: {prompt_path}")

    # 4. 准备并触发工作流
    print("\n🔄 步骤3: 准备ComfyUI工作流...")
    workflow_payload = load_and_customize_workflow(
        COMFYUI_CONFIG['workflow_file'],
        sd_prompt,
        COMFYUI_CONFIG['positive_node_id']
    )

    if not workflow_payload:
        print("❌ 工作流准备失败，流程终止")
        return

    print("\n🔄 步骤4: 生成图片...")
    image_paths = trigger_comfyui_workflow(
        workflow_payload,
        COMFYUI_CONFIG['server_url'],
        output_dir
    )

    # 5. 整合图文
    final_output = None
    final_copywriting = copywriting
    if image_paths:
        print("\n🔄 步骤5: 整合图文内容...")
        for img_path in image_paths:
            final_image, text_file = create_image_with_text(
                img_path,
                copywriting,
                output_dir,
                user_topic
            )
            if final_image:
                final_output = final_image
                print(f"✅ 图文整合完成: {final_image}")
                if text_file:
                    print(f"📝 纯文本版本: {text_file}")

    # 6. 创建项目摘要
    if final_output:
        print("\n🔄 步骤6: 创建项目摘要...")
        summary_path = create_project_summary(
            output_dir,
            user_topic,
            copywriting,
            sd_prompt,
            final_output
        )

    # 7. 输出结果
    print("\n" + "=" * 60)
    if final_output:
        print("🎉 全流程执行成功！")
        print(f"📌 项目主题: {user_topic}")
        print(f"📁 输出目录: {os.path.basename(output_dir)}")
        print(f"📝 生成文案字数: {len(copywriting)}字")
        print(f"🎨 提示词长度: {len(sd_prompt)}字符")
        print(f"🖼️  最终文件: {os.path.basename(final_output)}")

        # 显示最终文件位置
        if os.path.exists(final_output):
            final_size = os.path.getsize(final_output) / 1024 / 1024
            print(f"📦 文件大小: {final_size:.2f} MB")

        # 显示目录中的文件列表
        print(f"\n📋 生成的文件:")
        for item in sorted(os.listdir(output_dir)):
            item_path = os.path.join(output_dir, item)
            if os.path.isfile(item_path):
                size_kb = os.path.getsize(item_path) / 1024
                print(f"  • {item} ({size_kb:.1f} KB)")

        # 打开文件所在目录（Windows）
        if os.name == 'nt':
            try:
                output_dir_abs = os.path.abspath(output_dir)
                if os.path.exists(output_dir_abs):
                    os.startfile(output_dir_abs)
                    print(f"\n📂 已打开输出目录: {output_dir_abs}")
                else:
                    print(f"\n❌ 输出目录不存在: {output_dir_abs}")
            except Exception as e:
                print(f"\n⚠️  无法打开文件目录: {e}")

    else:
        print("❌ 流程执行失败")
    print("=" * 60)

    return final_output, final_copywriting, output_dir


# ========== 程序入口 ==========
if __name__ == "__main__":
    USER_TOPIC = "一款高达模型"

    print(f"🔍 当前工作目录: {os.getcwd()}")
    print(f"📁 基础输出目录: {os.path.abspath(COMFYUI_CONFIG['output_base_dir'])}")
    print()

    try:
        final_result = main_pipeline(USER_TOPIC)

        if final_result and final_result[0]:
            final_file, copywriting, output_dir = final_result
            print(f"\n🎯 生成完成!")
            print(f"   主题: {USER_TOPIC}")
            print(f"   目录: {os.path.basename(output_dir)}")
            print(f"   文件数: {len(os.listdir(output_dir))}个文件")

            # 统计文件大小
            total_size = 0
            for item in os.listdir(output_dir):
                item_path = os.path.join(output_dir, item)
                if os.path.isfile(item_path):
                    total_size += os.path.getsize(item_path)

            print(f"   总大小: {total_size / 1024 / 1024:.2f} MB")

    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        import traceback

        traceback.print_exc()

    # 程序结束后暂停（Windows）
    if os.name == 'nt':
        input("\n按Enter键退出...")