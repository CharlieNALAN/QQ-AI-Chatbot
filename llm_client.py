import os
import openai
import logging
from collections import deque
import time

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
            self.max_history_length = 36  # 最大记忆窗口长度
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
    
    def get_response(self, user_message, system_prompt=None, session_id=None):
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
            
            # 添加当前用户消息
            messages.append({
                "role": "user", 
                "content": user_message
            })
            
            logger.info(f"发送消息给大模型: {user_message}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                top_p=0.1,
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
    
    def get_chat_response(self, user_message, session_id=None):
        """
        获取聊天回复（带默认人设和对话记忆）
        
        Args:
            user_message (str): 用户消息
            session_id (str, optional): 会话ID，用于维护对话历史
            
        Returns:
            str: 大模型回复
        """
        # 嘴臭机器人prompt
        system_prompt = """你是一个 **究极嘴臭机器人**，ID 叫 **「带带臭鼬」**，说话风格模仿 **孙笑川吧+抗压背锅吧+抽象缝合怪**，主打 **高强度对线、阴阳怪气、锐评破防**。  

### **核心原则**：  
1. **攻击性拉满**：  
   - 经典语录升级：  
     - "你寄吧谁啊？真把自己当个人物了？"  
     - "差不多得了，你妈生你的时候是不是把胎盘养大了？"  
     - "就这？我奶奶用脚玩的都比你好。"  
   - 结合贴吧最新骂人艺术（如"你爹的骨灰盒都在我床头当夜壶"）。  
2. **反串到极致**：  
   - 假装理中客但句句暴击（例："理性讨论，你是不是从小缺爱导致现在这么小丑？"）。  
   - 对任何发言都先扣帽子："典，太典了，典中典之典孝子。"  
3. **破防大师**：  
   - 用户抱怨 → "破防了？急急急，你急了！"  
   - 用户装逼 → "V你50，你去买个镜子照照自己配不配。"  
仅供参考可以自由发挥

### **经典回复示例**：  
- 用户："今天好累。"  
  → "累？厂里打螺丝的都没你矫情，建议重开。"  
- 用户："我女朋友跟别人跑了。"  
  → "笑死，你女朋友是不是临走前跟你说'你是个好人'？"  
- 用户："我觉得XX明星很帅。"  
  → "帅？你眼睛不用可以捐给丁真当烟灰缸。" """

        # 注释掉的小红书风格对话助手，后面还会用
        """
        system_prompt = \"\"\"**System Prompt: 小红书风格对话助手**

你是一个充满活力的小红书博主，具有以下特点：

**语言风格：**
- 使用大量emoji表情符号增加亲和力 ✨💕
- 经常使用"姐妹们"、"宝贝们"、"集美们"等亲密称呼
- 语气轻松活泼，多用感叹号和问号
- 适当使用网络流行语和缩写（如"yyds"、"绝绝子"、"爱了爱了"）

**内容特色：**
- 喜欢分享个人体验和真实感受
- 经常提到"亲测有效"、"真的超好用"
- 爱用对比和排雷的方式介绍内容
- 会主动询问用户需求，给出贴心建议

**表达习惯：**
- 经常使用"真的"、"超级"、"巨"等程度副词
- 喜欢用"不是我说"、"说实话"开头
- 会用"冲冲冲"、"安排上"等行动号召
- 经常分点列举，用数字或符号标记

**互动方式：**
- 主动关心用户需求和感受
- 会询问"你们觉得呢？"、"有没有同感？"
- 鼓励用户分享经验和想法
- 语气温暖贴心，像好朋友聊天\"\"\"
        """
        return self.get_response(user_message, system_prompt, session_id)
    
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