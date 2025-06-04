import json
import requests
import random
from flask import Flask, request, jsonify
import logging
from llm_client import llm_client
from utils import (
    get_session_style, 
    parse_system_command, 
    handle_system_command,
    ban_list,
    handle_banned_user,
    probabilitys
)
from api import api_bp

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 注册API蓝图
app.register_blueprint(api_bp)

# napcat配置
NAPCAT_HOST = "127.0.0.1"
NAPCAT_PORT = 3000
NAPCAT_URL = f"http://{NAPCAT_HOST}:{NAPCAT_PORT}"

def send_message(user_id=None, group_id=None, message=""):
    """发送消息到QQ"""
    try:
        if group_id:
            # 发送群消息
            url = f"{NAPCAT_URL}/send_group_msg"
            data = {
                "group_id": group_id,
                "message": message
            }
        elif user_id:
            # 发送私聊消息
            url = f"{NAPCAT_URL}/send_private_msg"
            data = {
                "user_id": user_id,
                "message": message
            }
        else:
            logger.error("必须指定user_id或group_id")
            return False
        
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            logger.info(f"消息发送成功: {message}")
            return True
        else:
            logger.error(f"消息发送失败: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"发送消息时出错: {e}")
        return False

@app.route('/', methods=['POST'])
def handle_message():
    """处理从napcat接收到的消息"""
    try:
        data = request.get_json()
        logger.info(f"收到消息: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        # 检查是否是消息事件
        if data.get('post_type') == 'message':
            message_type = data.get('message_type')
            message = data.get('message', [])
            user_id = data.get('user_id')
            
            # 获取机器人自己的QQ号
            self_id = data.get('self_id')
            
            # 处理消息数组格式
            message_text = ""
            is_at_bot = False
            
            if isinstance(message, list):
                # 消息是数组格式，需要解析
                for msg_seg in message:
                    if isinstance(msg_seg, dict):
                        if msg_seg.get('type') == 'text':
                            message_text += msg_seg.get('data', {}).get('text', '')
                        elif msg_seg.get('type') == 'at':
                            # 检查@的目标是否是机器人自己
                            at_qq = msg_seg.get('data', {}).get('qq')
                            if str(at_qq) == str(self_id):
                                is_at_bot = True
                                logger.info(f"检测到@机器人: {at_qq} == {self_id}")
            elif isinstance(message, str):
                # 消息是字符串格式
                message_text = message
                # 对于字符串格式，检查是否包含@机器人的CQ码
                if self_id and f'[CQ:at,qq={self_id}]' in message:
                    is_at_bot = True
                elif message.strip().startswith('@'):
                    # 简单的@检测（不够精确，建议使用数组格式）
                    is_at_bot = True
            
            logger.info(f"机器人QQ号: {self_id}")
            logger.info(f"解析后的消息文本: {message_text}")
            logger.info(f"是否@机器人: {is_at_bot}")
            
            if message_type == 'group':
                # 群消息处理
                group_id = data.get('group_id')
                session_id = f"group_{group_id}"
                # 检查用户发言是否包含ban_list中的关键字
                message_lower = message_text.lower().replace(" ", "")
                is_banned = any(banned_word in message_lower for banned_word in ban_list if banned_word.strip())
                
                if is_banned:
                    handle_banned_user(NAPCAT_URL, group_id, user_id, send_message)
                
                # 只有@机器人时才回复
                if is_at_bot and message_text.strip():
                    logger.info(f"机器人被@了，群号: {group_id}, 用户: {user_id}")
                    
                    # 检查是否是系统命令
                    is_command, command, params = parse_system_command(message_text.strip())
                    
                    
                    if is_command:
                        # 处理系统命令
                        logger.info(f"检测到系统命令: {command} {params}")
                        reply = handle_system_command(command, params, session_id)
                        send_message(group_id=group_id, message=reply)
                    else:
                        # 使用大模型生成回复
                        try:
                            if llm_client:
                                # 获取当前会话的风格
                                current_style = get_session_style(session_id)
                                ai_reply = llm_client.get_chat_response(message_text.strip(), session_id, current_style)
                            else:
                                ai_reply = "抱歉，AI服务暂时不可用。"
                            send_message(group_id=group_id, message=ai_reply)
                        except Exception as e:
                            logger.error(f"大模型调用失败: {e}")
                            # 降级到默认回复
                            send_message(group_id=group_id, message="抱歉，我现在无法回复，请稍后再试。")
                else:
                    # 没有@机器人，但有5%概率自动回复
                    if message_text.strip() and random.random() < probabilitys.get(session_id, 0.05):
                        logger.info(f"触发5%概率自动回复，群号: {group_id}, 用户: {user_id}")
                        session_id = f"group_{group_id}"
                        
                        # 使用大模型生成回复
                        try:
                            if llm_client:
                                # 获取当前会话的风格
                                current_style = get_session_style(session_id)
                                ai_reply = llm_client.get_chat_response(message_text.strip(), session_id, current_style, auto_reply=True)
                            else:
                                ai_reply = "抱歉，AI服务暂时不可用。"
                            send_message(group_id=group_id, message=ai_reply)
                        except Exception as e:
                            logger.error(f"大模型调用失败: {e}")
                            # 降级到默认回复
                            send_message(group_id=group_id, message="emmm...")
                    else:
                        logger.info(f"群消息但未@机器人或消息为空，忽略")
                    
            elif message_type == 'private':
                # 私聊消息处理
                logger.info(f"收到私聊消息，用户: {user_id}")
                
                if message_text.strip():
                    # 检查是否是系统命令
                    is_command, command, params = parse_system_command(message_text.strip())
                    session_id = f"private_{user_id}"
                    
                    if is_command:
                        # 处理系统命令
                        logger.info(f"检测到系统命令: {command} {params}")
                        reply = handle_system_command(command, params, session_id)
                        send_message(user_id=user_id, message=reply)
                    else:
                        # 使用大模型生成回复
                        try:
                            if llm_client:
                                # 获取当前会话的风格
                                current_style = get_session_style(session_id)
                                ai_reply = llm_client.get_chat_response(message_text.strip(), session_id, current_style)
                            else:
                                ai_reply = "抱歉，AI服务暂时不可用。"
                            send_message(user_id=user_id, message=ai_reply)
                        except Exception as e:
                            logger.error(f"大模型调用失败: {e}")
                            # 降级到默认回复
                            send_message(user_id=user_id, message="抱歉，我现在无法回复，请稍后再试。")
        
        return jsonify({"status": "ok"})
        
    except Exception as e:
        logger.error(f"处理消息时出错: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    logger.info("启动QQ机器人...")
    logger.info("请确保napcat已启动并配置正确")
    logger.info("请设置环境变量 OPENAI_API_KEY 和 BASE_URL")
    logger.info(f"Bot服务器启动在: http://0.0.0.0:5000")
    logger.info(f"napcat地址: {NAPCAT_URL}")
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000, debug=True)
