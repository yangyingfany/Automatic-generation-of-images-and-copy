import requests
import json
import time
import os

# ========== 用户配置区 ==========
COZE_CONFIG = {
    "bot_id": "7584493784956796974",  # 需要用户修改
    "api_key": "pat_ivmwvr7EwaQbUb9ZqonpvZYjXLpjTOi1Dt9w5kwehdbI66Bxh06344to4U6QsjGz"  # 需要用户修改
}
DEEPSEEK_API_KEY = "sk-7b64922f9d6848f99f53204229c9cddb"  # 需要用户修改
COMFYUI_CONFIG = {
    "server_url": "http://127.0.0.1:8188",
    "workflow_file": "test1.json",
    "positive_node_id": "1",
    "output_dir": "./comfyui_outputs"
}


# ========== Coze文案生成 ==========
def generate_copywriting_with_coze(prompt, bot_id, api_key):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    chat_url = "https://api.coze.cn/v3/chat"

    chat_data = {
        "bot_id": bot_id,
        "user_id": "user_123456",
        "stream": False,
        "auto_save_history": True,
        "additional_messages": [{"role": "user", "content": prompt, "content_type": "text"}]
    }

    try:
        resp = requests.post(chat_url, headers=headers, json=chat_data, timeout=30)
        chat_result = resp.json()
        if chat_result.get("code") != 0:
            print(f"❌ Coze对话失败: {chat_result.get('msg')}")
            return None

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

        # 获取AI回复
        list_msg_url = "https://api.coze.cn/v3/chat/message/list"
        params = {"chat_id": chat_id, "conversation_id": conversation_id}
        resp = requests.get(list_msg_url, headers=headers, params=params, timeout=30)
        msg_result = resp.json()

        if msg_result.get("code") == 0:
            for msg in msg_result.get("data", []):
                if msg.get("role") == "assistant" and msg.get("type") == "answer":
                    return msg.get("content", "").strip()
        return None

    except Exception as e:
        print(f"❌ Coze API错误: {e}")
        return None


# ========== DeepSeek提示词优化 ==========
def optimize_prompt_with_deepseek(original_text, api_key):
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
        return optimized_prompt.replace('```', '').replace('prompt:', '').strip()
    except Exception as e:
        print(f"❌ DeepSeek API错误: {e}")
        return None


# ========== 简化的工作流转换 ==========
def load_and_customize_workflow(workflow_file, positive_prompt, node_id):
    try:
        print("📋 构建工作流（简化版）...")

        # 直接硬编码连接
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
        return None


# ========== ComfyUI 工作流触发 ==========
def trigger_comfyui_workflow(workflow_payload, server_url, output_dir):
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

        resp = requests.post(queue_url, json={"prompt": workflow_payload}, timeout=30)

        if resp.status_code != 200:
            error_data = resp.json()
            print(f"❌ 提交失败: {error_data.get('error', {}).get('message', '未知错误')}")
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
                        save_path = os.path.join(output_dir, f"comfy_{timestamp}_{prompt_id[:6]}.png")
                        with open(save_path, 'wb') as f:
                            f.write(image_resp.content)
                        images_output.append(save_path)
                        print(f"💾 图片已保存: {save_path}")

        return images_output if images_output else None

    except Exception as e:
        print(f"❌ 图片下载失败: {e}")
        return None


# ========== 主流程 ==========
def main_pipeline(user_topic):
    print("=" * 60)
    print("启动AIGC生成流水线")
    print("=" * 60)

    # 1. 生成文案
    print("🔄 步骤1: 生成文案...")
    copywriting = generate_copywriting_with_coze(user_topic, COZE_CONFIG["bot_id"], COZE_CONFIG["api_key"])
    if not copywriting:
        print("❌ 文案生成失败，流程终止")
        return False
    print(f"✅ 文案生成成功: {copywriting[:50]}...")

    # 2. 优化提示词
    print("\n🔄 步骤2: 优化提示词...")
    sd_prompt = optimize_prompt_with_deepseek(copywriting, DEEPSEEK_API_KEY)
    if not sd_prompt:
        print("❌ 提示词优化失败，流程终止")
        return False
    print(f"✅ 提示词优化成功: {sd_prompt[:50]}...")

    # 3. 准备并触发工作流
    print("\n🔄 步骤3: 准备ComfyUI工作流...")
    workflow_payload = load_and_customize_workflow(
        COMFYUI_CONFIG['workflow_file'],
        sd_prompt,
        COMFYUI_CONFIG['positive_node_id']
    )

    if not workflow_payload:
        print("❌ 工作流准备失败，流程终止")
        return False

    print("\n🔄 步骤4: 生成图片...")
    image_paths = trigger_comfyui_workflow(
        workflow_payload,
        COMFYUI_CONFIG['server_url'],
        COMFYUI_CONFIG['output_dir']
    )

    # 4. 输出结果
    print("\n" + "=" * 60)
    if image_paths:
        print("🎉 全流程执行成功！")
        print(f"📝 生成文案: {copywriting[:80]}...")
        print(f"🎨 使用提示词: {sd_prompt[:80]}...")
        print(f"🖼️  图片保存至: {image_paths[0]}")
        return True
    else:
        print("❌ 图片生成失败")
        return False


# ========== 程序入口 ==========
if __name__ == "__main__":
    USER_TOPIC = "一款高达模型"
    
    try:
        # 运行主流程
        final_result = main_pipeline(USER_TOPIC)
        
        # 等待用户查看结果
        if final_result:
            print("=" * 60)
            print("✅ 所有任务已完成！")
        else:
            print("=" * 60)
            print("❌ 流程执行失败")
            
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 保持窗口不关闭
    input("\n按Enter键退出...")
