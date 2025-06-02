import re
import logging

logger = logging.getLogger(__name__)

# 存储每个会话的风格设置，默认为嘴臭风格
session_styles = {}

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
        return "可用命令：\n[切换风格 风格名]\n[风格列表]\n[帮助]"
    
    return "未知的系统命令"

def get_available_styles():
    """获取所有可用的风格"""
    from prompts import prompt_mp
    return list(prompt_mp.keys())

def get_all_session_styles():
    """获取所有会话的风格设置"""
    return session_styles.copy() 