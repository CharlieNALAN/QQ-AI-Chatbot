import colorlog

class CustomColoredFormatter(colorlog.ColoredFormatter):
    def format(self, record):
        # 保存原始消息
        original_msg = record.msg
        
        # 使用ANSI颜色代码
        GREEN = '\033[32m'
        BLUE = '\033[34m'
        RED = '\033[31m'
        YELLOW = '\033[33m'
        CYAN = '\033[36m'
        WHITE = '\033[37m'
        RESET = '\033[0m'
        
        # 格式化时间戳
        time_str = self.formatTime(record, self.datefmt)
        colored_time = f'{GREEN}{time_str}{RESET}'
        
        # 设置logger名称为蓝色
        colored_name = f'{BLUE}{record.name}{RESET}'
        
        # 根据日志级别设置颜色
        if record.levelname == 'INFO':
            colored_level = f'{GREEN}{record.levelname}{RESET}'
        elif record.levelname == 'ERROR':
            colored_level = f'{RED}{record.levelname}{RESET}'
        elif record.levelname == 'WARNING':
            colored_level = f'{YELLOW}{record.levelname}{RESET}'
        elif record.levelname == 'DEBUG':
            colored_level = f'{CYAN}{record.levelname}{RESET}'
        else:
            colored_level = record.levelname
            
        # 消息内容保持白色
        colored_msg = f'{WHITE}{original_msg}{RESET}'
        
        # 组合最终的日志消息
        record.msg = f'[{colored_time}][{colored_name}][{colored_level}] - {colored_msg}'
        return record.msg 