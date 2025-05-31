import json
import requests
from flask import Flask, request, jsonify
import logging
from llm_client import llm_client

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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
                
                # 只有@机器人时才回复
                if is_at_bot and message_text.strip():
                    logger.info(f"机器人被@了，群号: {group_id}, 用户: {user_id}")
                    
                    # 使用大模型生成回复，传入群组ID作为会话ID
                    try:
                        if llm_client:
                            # 使用 "group_" + group_id 作为群聊的会话ID
                            session_id = f"group_{group_id}"
                            ai_reply = llm_client.get_chat_response(message_text.strip(), session_id)
                        else:
                            ai_reply = "抱歉，AI服务暂时不可用。"
                        send_message(group_id=group_id, message=ai_reply)
                    except Exception as e:
                        logger.error(f"大模型调用失败: {e}")
                        # 降级到默认回复
                        send_message(group_id=group_id, message="抱歉，我现在无法回复，请稍后再试。")
                else:
                    logger.info(f"群消息但未@机器人或消息为空，忽略")
                    
            elif message_type == 'private':
                # 私聊消息处理
                logger.info(f"收到私聊消息，用户: {user_id}")
                
                if message_text.strip():
                    # 使用大模型生成回复，传入用户ID作为会话ID
                    try:
                        if llm_client:
                            # 使用 "private_" + user_id 作为私聊的会话ID
                            session_id = f"private_{user_id}"
                            ai_reply = llm_client.get_chat_response(message_text.strip(), session_id)
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

@app.route('/test', methods=['GET'])
def test():
    """测试接口"""
    return jsonify({"status": "Bot is running!", "message": "QQ机器人正常运行"})

@app.route('/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """获取指定会话的历史记录"""
    try:
        if llm_client:
            history_length = llm_client.get_history_length(session_id)
            from llm_client import cache_history
            history = list(cache_history.get(session_id, []))
            return jsonify({
                "status": "success",
                "session_id": session_id,
                "history_length": history_length,
                "history": history
            })
        else:
            return jsonify({"status": "error", "message": "LLM客户端不可用"}), 500
    except Exception as e:
        logger.error(f"获取历史记录失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/history/<session_id>', methods=['DELETE'])
def clear_history(session_id):
    """清空指定会话的历史记录"""
    try:
        if llm_client:
            llm_client.clear_history(session_id)
            return jsonify({
                "status": "success",
                "message": f"已清空会话 {session_id} 的历史记录"
            })
        else:
            return jsonify({"status": "error", "message": "LLM客户端不可用"}), 500
    except Exception as e:
        logger.error(f"清空历史记录失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/history/all', methods=['GET'])
def get_all_sessions():
    """获取所有会话的信息"""
    try:
        from llm_client import cache_history, cache_time
        import time
        
        sessions_info = {}
        current_time = time.time()
        
        for session_id, history in cache_history.items():
            last_active_time = cache_time.get(session_id)
            time_since_last_active = None
            if last_active_time:
                time_since_last_active = current_time - last_active_time
            
            sessions_info[session_id] = {
                "length": len(history),
                "last_message": history[-1]["content"] if history else None,
                "last_active_time": last_active_time,
                "time_since_last_active_minutes": time_since_last_active / 60 if time_since_last_active else None
            }
            
        return jsonify({
            "status": "success",
            "total_sessions": len(sessions_info),
            "sessions": sessions_info
        })
    except Exception as e:
        logger.error(f"获取会话信息失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/session/<session_id>/info', methods=['GET'])
def get_session_info(session_id):
    """获取指定会话的详细信息，包括时间戳"""
    try:
        if llm_client:
            session_info = llm_client.get_session_info(session_id)
            return jsonify({
                "status": "success",
                **session_info
            })
        else:
            return jsonify({"status": "error", "message": "LLM客户端不可用"}), 500
    except Exception as e:
        logger.error(f"获取会话信息失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    logger.info("启动QQ机器人...")
    logger.info("请确保napcat已启动并配置正确")
    logger.info("请设置环境变量 SAMBANOVA_API_KEY")
    logger.info(f"Bot服务器启动在: http://0.0.0.0:5000")
    logger.info(f"napcat地址: {NAPCAT_URL}")
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000, debug=True)
