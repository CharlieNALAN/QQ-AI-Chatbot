from flask import Blueprint, jsonify, request
import logging
from llm_client import llm_client, cache_history, cache_time
from utils import get_session_style, set_session_style, get_available_styles, get_all_session_styles
import time

logger = logging.getLogger(__name__)

# 创建API蓝图
api_bp = Blueprint('api', __name__)

@api_bp.route('/test', methods=['GET'])
def test():
    """测试接口"""
    return jsonify({"status": "Bot is running!", "message": "QQ机器人正常运行"})

@api_bp.route('/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """获取指定会话的历史记录"""
    try:
        if llm_client:
            history_length = llm_client.get_history_length(session_id)
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

@api_bp.route('/history/<session_id>', methods=['DELETE'])
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

@api_bp.route('/history/all', methods=['GET'])
def get_all_sessions():
    """获取所有会话的信息"""
    try:
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

@api_bp.route('/session/<session_id>/info', methods=['GET'])
def get_session_info(session_id):
    """获取指定会话的详细信息，包括时间戳"""
    try:
        if llm_client:
            session_info = llm_client.get_session_info(session_id)
            # 添加风格信息
            session_info["current_style"] = get_session_style(session_id)
            return jsonify({
                "status": "success",
                **session_info
            })
        else:
            return jsonify({"status": "error", "message": "LLM客户端不可用"}), 500
    except Exception as e:
        logger.error(f"获取会话信息失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route('/styles', methods=['GET'])
def get_available_styles_api():
    """获取所有可用的风格"""
    try:
        available_styles = get_available_styles()
        return jsonify({
            "status": "success",
            "available_styles": available_styles,
            "total_count": len(available_styles)
        })
    except Exception as e:
        logger.error(f"获取可用风格失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route('/session/<session_id>/style', methods=['GET'])
def get_session_style_api(session_id):
    """获取指定会话的当前风格"""
    try:
        current_style = get_session_style(session_id)
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "current_style": current_style
        })
    except Exception as e:
        logger.error(f"获取会话风格失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route('/session/<session_id>/style', methods=['POST'])
def set_session_style_api(session_id):
    """设置指定会话的风格"""
    try:
        data = request.get_json()
        style = data.get('style')
        
        if not style:
            return jsonify({"status": "error", "message": "请提供style参数"}), 400
        
        # 检查风格是否存在
        available_styles = get_available_styles()
        
        if style not in available_styles:
            return jsonify({
                "status": "error", 
                "message": f"风格 '{style}' 不存在。可用风格：{', '.join(available_styles)}"
            }), 400
        
        set_session_style(session_id, style)
        return jsonify({
            "status": "success",
            "message": f"已将会话 {session_id} 切换到 {style} 风格",
            "session_id": session_id,
            "new_style": style
        })
    except Exception as e:
        logger.error(f"设置会话风格失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route('/styles/sessions', methods=['GET'])
def get_all_session_styles_api():
    """获取所有会话的风格设置"""
    try:
        session_styles = get_all_session_styles()
        return jsonify({
            "status": "success",
            "session_styles": session_styles,
            "total_sessions": len(session_styles)
        })
    except Exception as e:
        logger.error(f"获取所有会话风格失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500 