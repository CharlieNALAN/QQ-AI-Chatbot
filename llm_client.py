import os
import openai
import logging
from collections import deque
import time
from prompts import prompt_mp

logger = logging.getLogger(__name__)
# 修改cache_history为字典，每个会话ID对应一个deque队列，最大长度30
cache_history = {}
cache_time = {}

class LLMClient:
    def __init__(self):
        """初始化LLM客户端"""
        try:
            self.client = openai.OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("BASE_URL")
            )
            self.model = "deepseek-v3"
            self.max_history_length = 38  # 最大记忆窗口长度
            self.session_timeout = 15 * 60  # 15分钟，单位：秒
            logger.info("LLM客户端初始化成功")
        except Exception as e:
            logger.error(f"LLM客户端初始化失败: {e}")
            self.client = None
    
    def _check_session_timeout(self, session_id):
        """检查会话是否超时，如果超时则清空历史记录"""
        current_time = time.time()
        
        if session_id in cache_time:
            last_time = cache_time[session_id]
            time_diff = current_time - last_time
            
            logger.info(f"会话 {session_id} 距离上次请求间隔: {time_diff:.1f} 秒")
            
            if time_diff > self.session_timeout:
                logger.info(f"会话 {session_id} 超过15分钟未活跃，清空历史记录")
                self.clear_history(session_id)
        
        # 更新当前会话的时间戳
        cache_time[session_id] = current_time
        logger.info(f"更新会话 {session_id} 时间戳: {current_time}")
    
    def _get_or_create_history(self, session_id):
        """获取或创建会话历史"""
        if session_id not in cache_history:
            cache_history[session_id] = deque(maxlen=self.max_history_length)
        return cache_history[session_id]
    
    def _add_to_history(self, session_id, role, content):
        """添加消息到历史记录"""
        history = self._get_or_create_history(session_id)
        history.append({"role": role, "content": content})
        logger.info(f"会话 {session_id} 历史记录长度: {len(history)}")
    
    def get_response(self, user_message, system_prompt=None, session_id=None, auto_reply=False):
        """
        获取大模型回复
        
        Args:
            user_message (str): 用户消息
            system_prompt (str, optional): 系统提示词
            session_id (str, optional): 会话ID，用于维护对话历史
        
        Returns:
            str: 大模型回复内容
        """
        if not self.client:
            return "抱歉，大模型服务未正确初始化。"
            
        try:
            # 如果有session_id，检查会话超时
            if session_id:
                self._check_session_timeout(session_id)
            
            messages = []
            
            # 添加系统提示词
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # 如果有session_id，添加历史对话
            if session_id:
                history = self._get_or_create_history(session_id)
                # 将历史对话添加到messages中
                messages.extend(list(history))
                logger.info(f"会话 {session_id} 加载了 {len(history)} 条历史记录")
            if auto_reply:
                new_user_message = "(你的回答不得超过20个字,尽可能用一句话回答,尽可能贴近人类聊天可能会打的文本样式,不携带引号和星号的标识符)" + user_message
            else:
                new_user_message = user_message

            # 添加当前用户消息
            messages.append({
                "role": "user", 
                "content": new_user_message
            })
            
            logger.info(f"发送消息给大模型: {new_user_message}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=1.0,
                top_p=1.0,
                max_tokens=1000
            )
            
            reply = response.choices[0].message.content
            logger.info(f"大模型回复: {reply}")
            
            # 如果有session_id，将用户消息和AI回复都保存到历史中
            if session_id:
                self._add_to_history(session_id, "user", user_message)
                self._add_to_history(session_id, "assistant", reply)
            
            return reply
            
        except Exception as e:
            logger.error(f"大模型请求失败: {e}")
            return "抱歉，我现在无法回复，请稍后再试。"
    
    def get_chat_response(self, user_message, session_id=None, style="嘴臭",auto_reply=False):
        """
        获取聊天回复（带默认人设和对话记忆）
        
        Args:
            user_message (str): 用户消息
            session_id (str, optional): 会话ID，用于维护对话历史
            style (str): 使用的风格，默认为嘴臭
            
        Returns:
            str: 大模型回复
        """
        # 根据风格选择对应的prompt
        system_prompt = prompt_mp.get(style, prompt_mp["嘴臭"])  # 如果风格不存在，使用默认嘴臭风格
        logger.info(f"使用风格: {style}")
        return self.get_response(user_message, system_prompt, session_id, auto_reply)
    
    def clear_history(self, session_id):
        """清空指定会话的历史记录"""
        if session_id in cache_history:
            cache_history[session_id].clear()
            logger.info(f"已清空会话 {session_id} 的历史记录")
        # 同时清空时间戳记录
        if session_id in cache_time:
            del cache_time[session_id]
            logger.info(f"已清空会话 {session_id} 的时间戳记录")
    
    def get_history_length(self, session_id):
        """获取指定会话的历史记录长度"""
        if session_id in cache_history:
            return len(cache_history[session_id])
        return 0
    
    def get_session_info(self, session_id):
        """获取会话详细信息，包括历史记录数量和最后活跃时间"""
        info = {
            "session_id": session_id,
            "history_length": self.get_history_length(session_id),
            "last_active_time": None,
            "time_since_last_active": None
        }
        
        if session_id in cache_time:
            last_time = cache_time[session_id]
            current_time = time.time()
            info["last_active_time"] = last_time
            info["time_since_last_active"] = current_time - last_time
        
        return info

# 创建全局实例
try:
    llm_client = LLMClient()
except Exception as e:
    logger.error(f"创建LLM客户端实例失败: {e}")
    llm_client = None 