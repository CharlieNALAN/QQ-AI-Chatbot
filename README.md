# QQ机器人项目 - AI智能对话系统

这是一个基于napcat和Python Flask的智能QQ机器人。机器人支持多种聊天风格、对话记忆、违禁词检测和自动禁言等功能。系统兼容所有OpenAI格式的API接口。

## 主要功能

- **智能对话**：机器人被@时会自动回复，支持上下文记忆
- **多风格切换**：支持嘴臭、小红书、标准三种聊天风格，可随时切换
- **违禁词检测**：自动检测违禁词并对发送者进行禁言处理
- **系统命令**：支持风格切换、风格列表、帮助等系统命令
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

## 机器人风格配置

机器人支持三种预设风格，可以通过系统命令实时切换：

### 默认风格设置

机器人启动时默认使用**嘴臭风格**。你可以通过以下方式修改：

1. **实时切换**：使用 `[切换风格 风格名]` 命令
2. **修改默认风格**：在 `utils.py` 中修改 `get_session_style` 函数的默认返回值

### 自定义风格

你可以在 `prompts.py` 中添加新的风格：

```python
# 添加新风格到 prompt_mp 字典
prompt_mp = {
    "嘴臭": abuse_attack_prompt,
    "小红书": rednote_prompt,
    "标准": normal_prompt,
    "你的风格": "你的自定义prompt..."
}
```

### 风格特点说明

- **嘴臭风格**：模仿贴吧文化，高强度对线，适合娱乐
- **小红书风格**：活泼可爱，大量emoji，亲和力强
- **标准风格**：正常AI助手，专业友好，适合正式场合

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

**注意**：机器人会自动检测群内违禁词，发送违禁词的用户会被自动禁言。

### 私聊使用

直接给机器人发送私聊消息。机器人会记住你们的对话历史。

### 系统命令

机器人支持以下系统命令（使用方括号格式）：

- **`[切换风格 风格名]`** - 切换聊天风格
  ```
  [切换风格 小红书]
  [切换风格 嘴臭]
  [切换风格 标准]
  ```

- **`[风格列表]`** - 查看所有可用风格
- **`[帮助]`** - 查看所有可用命令

### 可用聊天风格

1. **嘴臭风格**：高强度对线、阴阳怪气风格，适合娱乐向群聊
2. **小红书风格**：活泼可爱、充满emoji的小姐姐风格
3. **标准风格**：正常友好的AI助手风格，适合日常对话

### 违禁词管理

- 机器人会自动监控群内消息
- 检测到违禁词会自动禁言发送者
- 禁言时间会根据用户违规次数递增
- 违禁词列表可在 `ban.txt` 中配置

### 对话记忆

机器人为每个用户和群维护独立的对话历史。超过15分钟无活动会自动清空历史。

## API管理接口

系统提供HTTP接口来管理对话会话和风格：

### 会话管理

#### 查看所有会话
```bash
GET http://127.0.0.1:5000/history/all
```

#### 查看指定会话历史
```bash
GET http://127.0.0.1:5000/history/<session_id>
```

#### 获取会话详细信息
```bash
GET http://127.0.0.1:5000/session/<session_id>/info
```

#### 清空会话历史
```bash
DELETE http://127.0.0.1:5000/history/<session_id>
```

### 风格管理

#### 查看所有会话的风格设置
```bash
GET http://127.0.0.1:5000/styles/all
```

#### 获取可用风格列表
```bash
GET http://127.0.0.1:5000/styles/available
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

### 违禁词配置

编辑 `ban.txt` 文件来管理违禁词列表：

```txt
违禁词1
违禁词2
违禁词3
```

调整禁言参数（在 `utils.py` 的 `ban_user` 函数中）：

```python
duration = 30  # 基础禁言时长（秒）
# 实际禁言时间 = duration * 用户违规次数
```

### 添加新的聊天风格

1. 在 `prompts.py` 中添加新的prompt
2. 更新 `prompt_mp` 字典
3. 重启机器人即可使用新风格

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

### 违禁词功能问题

1. 检查 `ban.txt` 文件是否存在且格式正确
2. 确认机器人在群内有管理员权限
3. 查看控制台是否有禁言失败的错误日志
4. 检验违禁词检测逻辑（大小写、空格等）

### 风格切换失败

1. 确认风格名称拼写正确（区分大小写）
2. 检查 `prompts.py` 中是否存在对应风格
3. 使用 `[风格列表]` 命令查看可用风格
4. 重启机器人后重试

## 项目结构

```
QQBot/
├── main.py              # 主程序和消息处理逻辑
├── llm_client.py        # AI客户端和对话记忆管理
├── utils.py             # 工具函数（禁言、风格管理等）
├── prompts.py           # 各种聊天风格的prompt定义
├── api.py               # API蓝图和管理接口
├── regular_dialog.py    # 违禁词处理的提示语
├── ban.txt              # 违禁词列表配置
├── requirements.txt     # Python依赖包
├── napcat_config.json   # napcat配置示例
└── README.md           # 项目文档
```

## 依赖包说明

- **Flask**：Web框架，处理HTTP请求
- **requests**：HTTP客户端，与napcat通信
- **openai**：OpenAI兼容的API客户端 