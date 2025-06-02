import re
import logging
import requests
from collections import Counter
import random    
from regular_dialog import ban, ban_fail
from llm_client import llm_client
from typing import Callable
logger = logging.getLogger(__name__)

# 存储每个会话的风格设置，默认为嘴臭风格
session_styles = {}

ban_list = set()
with open("ban.txt", "r") as f:
    ban_list = f.readlines()
    ban_list = set([line.strip() for line in ban_list])

user_ban_times = Counter()

def get_session_style(session_id):
    """获取指定会话的风格，默认为嘴臭风格"""
    return session_styles.get(session_id, "嘴臭")

def set_session_style(session_id, style):
    """设置指定会话的风格"""
    session_styles[session_id] = style
    logger.info(f"会话 {session_id} 风格已切换为: {style}")

def parse_system_command(message_text):
    """
    解析系统命令
    格式: [命令 参数]
    返回: (is_command, command, params) 或 (False, None, None)
    """
    # 匹配 [xxx] 格式的系统命令
    pattern = r'^\[(.+?)\]'
    match = re.match(pattern, message_text.strip())
    
    if match:
        command_content = match.group(1).strip()
        
        # 解析切换风格命令
        if command_content.startswith("切换风格"):
            parts = command_content.split()
            if len(parts) >= 2:
                style_name = parts[1]
                return True, "切换风格", style_name
            else:
                return True, "切换风格", None
        
        # 可以在这里添加更多系统命令
        # 解析风格列表命令
        elif command_content == "风格列表":
            return True, "风格列表", None
        
        elif command_content == "帮助":
            return True, "帮助", None
        
    return False, None, None

def handle_system_command(command, params, session_id):
    """处理系统命令"""
    if command == "切换风格":
        if params is None:
            return "请指定要切换的风格，例如：[切换风格 小红书]"
        
        # 检查风格是否存在
        from prompts import prompt_mp
        available_styles = list(prompt_mp.keys())
        
        if params not in available_styles:
            return f"风格 '{params}' 不存在。可用风格：{', '.join(available_styles)}"
        
        # 设置风格
        set_session_style(session_id, params)
        return f"已切换到 {params} 风格！"
    if command == "风格列表":
        return "可用风格：" + ", ".join(get_available_styles())
    
    if command == "帮助":
        return "可用命令：\n[切换风格 <风格名>]\n[风格列表]\n[帮助]"
    
    return "未知的系统命令"

def get_available_styles():
    """获取所有可用的风格"""
    from prompts import prompt_mp
    return list(prompt_mp.keys())

def get_all_session_styles():
    """获取所有会话的风格设置"""
    return session_styles.copy() 

def ban_user(url,group_id, user_id, duration = 30):
    user_ban_times[user_id] += 1
    duration = duration * user_ban_times[user_id]
    time = random.randint(1, duration)
    data = {
        "group_id": group_id,
        "user_id": user_id,
        "duration": time
    }
    response = requests.post(url+"/set_group_ban", json=data).json()
    return response["status"]

def handle_banned_user(napcat_url, group_id, user_id, send_message_func: Callable):
    """
    处理用户发送违禁词的逻辑
    
    Args:
        napcat_url (str): napcat服务的URL
        group_id (int): 群组ID
        user_id (int): 用户ID
        llm_client: 大模型客户端
        send_message_func: 发送消息的函数
    """

    
    # 尝试禁言用户
    status = ban_user(napcat_url, group_id, user_id)
    
    if status == "ok":
        logger.info(f"用户 {user_id} 已被禁言")
        # 使用大模型生成回复
        try:
            if llm_client:
                ai_reply = llm_client.get_chat_response(ban)
            else:
                ai_reply = "抱歉，AI服务暂时不可用。"
            send_message_func(group_id=group_id, message=ai_reply)
        except Exception as e:
            logger.error(f"大模型调用失败: {e}")
            # 降级到默认回复
            send_message_func(group_id=group_id, message="你已被禁言，请不要发送违禁词。")
    else:
        logger.error(f"禁言失败: {status}")
        # 使用大模型生成回复
        try:
            if llm_client:
                ai_reply = llm_client.get_chat_response(ban_fail)
            else:
                ai_reply = "抱歉，AI服务暂时不可用。"
            send_message_func(group_id=group_id, message=ai_reply)
        except Exception as e:
            logger.error(f"大模型调用失败: {e}")
            # 降级到默认回复
            send_message_func(group_id=group_id, message="你已被警告，请不要发送违禁词。")

if __name__ == "__main__":
    res = ban_user("http://127.0.0.1:3000", 1047399248, 1277087689, duration=1)
    print(res)