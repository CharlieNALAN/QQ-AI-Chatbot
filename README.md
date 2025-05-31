# QQ机器人项目 - AI智能对话系统

这是一个基于napcat和Python Flask的智能QQ机器人。机器人支持对话记忆功能。系统兼容所有OpenAI格式的API接口。

## 主要功能

- **智能对话**：机器人被@时会自动回复
- **记忆对话**：机器人记住每个用户和群的聊天历史
- **多平台支持**：支持群聊和私聊消息处理
- **API兼容**：支持OpenAI、DeepSeek、ChatAnywhere等所有兼容接口
- **会话管理**：15分钟无活动自动清空历史记录
- **HTTP通信**：基于HTTP API与napcat通信

## 前置要求

⚠️ **重要提醒**：本项目需要配合 [NapCatQQ](https://github.com/NapNeko/NapCatQQ) 框架使用。

### 安装NapCatQQ

在使用本机器人之前，你需要先安装和配置NapCatQQ：

1. **下载NapCatQQ**：访问 [NapCatQQ官方仓库](https://github.com/NapNeko/NapCatQQ) 下载最新版本
2. **查看文档**：参考 [官方文档](https://napneko.github.io/) 进行安装和配置
3. **启动服务**：确保NapCatQQ正常运行并配置好QQ登录

### NapCatQQ配置要求

- 启用HTTP服务器（端口3000）
- 配置HTTP客户端上报到Python程序（端口5000）
- 正确登录QQ账号

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

本项目通过环境变量来配置API，无需修改代码文件。设置以下环境变量：

```bash
# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
export BASE_URL="https://your-api-base-url"

# Windows (CMD)
set OPENAI_API_KEY=your-api-key-here
set BASE_URL=https://your-api-base-url

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"
$env:BASE_URL="https://your-api-base-url"
```

**或创建 `.env` 文件**（推荐）：
```env
OPENAI_API_KEY=your-api-key-here
BASE_URL=https://your-api-base-url
```

### 常用API配置示例

**OpenAI官方**：
```env
OPENAI_API_KEY=sk-xxx
BASE_URL=https://api.openai.com/v1
```

**DeepSeek**：
```env
OPENAI_API_KEY=sk-xxx
BASE_URL=https://api.deepseek.com/v1
```

**ChatAnywhere代理**：
```env
OPENAI_API_KEY=sk-xxx
BASE_URL=https://api.chatanywhere.tech/v1
```

**本地API（如Ollama）**：
```env
OPENAI_API_KEY=not-needed
BASE_URL=http://localhost:11434/v1
```

### 3. 配置napcat

将 `napcat_config.json` 的内容复制到你的napcat配置文件。主要设置包括：

- 开启HTTP服务器（端口3000）
- 配置HTTP客户端上报到Python程序（端口5000）
- 启用调试模式

### 4. 启动服务

先启动Python程序：
```bash
python main.py
```

然后启动napcat服务。

## 机器人人设配置

机器人当前使用嘴臭风格人设。你可以在 `llm_client.py` 的 `get_chat_response` 方法中修改 `system_prompt` 来更换人设。

### 切换到小红书风格

取消注释小红书风格prompt，注释掉嘴臭机器人prompt即可。

### 自定义人设

你可以编写自己的system_prompt来定义机器人的性格和回复风格。

## 配置详情

### napcat关键配置

```json
{
  "httpServers": [{
    "enable": true,
    "host": "127.0.0.1",
    "port": 3000
  }],
  "httpClients": [{
    "enable": true,
    "url": "http://127.0.0.1:5000",
    "timeout": 5000
  }]
}
```

### Python程序配置

- **监听端口**：5000
- **napcat地址**：http://127.0.0.1:3000
- **历史记录**：最大36条对话记录
- **会话超时**：15分钟无活动自动清空

## 使用方法

### 群聊使用

在QQ群中@机器人并发送消息。机器人会自动回复。每个群的对话历史独立保存。

### 私聊使用

直接给机器人发送私聊消息。机器人会记住你们的对话历史。

### 对话记忆

机器人为每个用户和群维护独立的对话历史。超过15分钟无活动会自动清空历史。

## API管理接口

系统提供HTTP接口来管理对话会话：

### 查看所有会话
```bash
GET http://127.0.0.1:5000/history/all
```

### 查看指定会话历史
```bash
GET http://127.0.0.1:5000/history/<session_id>
```

### 获取会话详细信息
```bash
GET http://127.0.0.1:5000/session/<session_id>/info
```

### 清空会话历史
```bash
DELETE http://127.0.0.1:5000/history/<session_id>
```

### 会话ID格式

- 群聊：`group_{群号}`
- 私聊：`private_{QQ号}`

## 测试与调试

### 程序状态测试
```bash
curl http://127.0.0.1:5000/test
```

### 查看运行日志

程序会在控制台输出详细的运行日志。包括：
- 接收到的消息内容
- AI回复生成过程
- 会话管理状态
- 错误信息

## 自定义扩展

### 修改AI参数

在 `llm_client.py` 中可以调整：

```python
temperature=0.1,    # 回复随机性（0-1）
top_p=0.1,         # 采样参数（0-1）
max_tokens=1000    # 最大回复长度
```

### 调整记忆设置

```python
self.max_history_length = 36    # 最大历史记录数
self.session_timeout = 15 * 60  # 会话超时时间（秒）
```

### 添加新功能

你可以在 `main.py` 中添加：
- 特殊指令处理
- 群管理功能
- 定时任务
- 数据库存储

## 故障排除

### 机器人不回复

1. 检查napcat是否正常启动
2. 查看Python控制台是否收到消息
3. 确认napcat配置正确
4. 检查端口是否被占用

### AI回复失败

1. 验证API密钥是否正确
2. 测试base_url是否可访问
3. 确认模型名称正确
4. 检查API额度是否充足

### 记忆功能异常

1. 查看控制台会话管理日志
2. 使用API接口检查会话状态
3. 手动清空异常会话历史

## 项目结构

```
QQBot/
├── main.py              # 主程序和API接口
├── llm_client.py        # AI客户端和对话记忆
├── requirements.txt     # Python依赖包
├── napcat_config.json   # napcat配置示例
└── README.md           # 项目文档
```

## 依赖包说明

- **Flask**：Web框架，处理HTTP请求
- **requests**：HTTP客户端，与napcat通信
- **openai**：OpenAI兼容的API客户端 