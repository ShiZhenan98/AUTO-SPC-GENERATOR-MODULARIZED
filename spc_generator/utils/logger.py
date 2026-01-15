"""日志系统配置"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional


class SPCLogger:
    """SPC工具日志管理器"""
    
    def __init__(self):
        self.logger: Optional[logging.Logger] = None
        self.log_file_path: Optional[str] = None
    
    def setup_logger(self, plan_name: str, log_directory: str = ".") -> logging.Logger:
        """
        设置日志系统
        
        Args:
            plan_name: 计划名称（用于日志文件名）
            log_directory: 日志文件保存目录
            
        Returns:
            配置好的Logger对象
        """
        # 生成日志文件名：计划名称 + 运行开始时间
        start_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 清理计划名称，移除非法字符
        safe_plan_name = self._sanitize_filename(plan_name)
        log_filename = f"{safe_plan_name}_{start_time_str}.log"
        
        # 确保日志目录存在
        os.makedirs(log_directory, exist_ok=True)
        self.log_file_path = os.path.join(log_directory, log_filename)
        
        # 创建Logger
        self.logger = logging.getLogger('SPCGenerator')
        self.logger.setLevel(logging.DEBUG)
        
        # 避免重复添加handler
        if self.logger.handlers:
            return self.logger
        
        # 创建文件handler
        file_handler = logging.FileHandler(
            self.log_file_path,
            mode='w',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 创建控制台handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建格式器
        # 文件日志格式：时间戳 - 级别 - 模块 - 行号 - 消息
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台日志格式：级别 - 消息
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
        # 添加handler到logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        return self.logger
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        清理文件名，移除非法字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的文件名
        """
        import re
        # 移除非法字符
        safe_name = re.sub(r'[\\/*?:"<>|]', '', filename)
        # 替换空格为下划线
        safe_name = safe_name.replace(' ', '_')
        # 限制长度
        if len(safe_name) > 100:
            safe_name = safe_name[:100]
        return safe_name
    
    def get_logger(self) -> Optional[logging.Logger]:
        """获取Logger对象"""
        return self.logger
    
    def get_log_file_path(self) -> Optional[str]:
        """获取日志文件路径"""
        return self.log_file_path


# 全局日志管理器实例
_logger_manager = SPCLogger()


def get_logger() -> Optional[logging.Logger]:
    """获取全局Logger对象"""
    return _logger_manager.get_logger()


def setup_logging(plan_name: str, log_directory: str = ".") -> logging.Logger:
    """
    设置全局日志系统
    
    Args:
        plan_name: 计划名称
        log_directory: 日志文件保存目录
        
    Returns:
        配置好的Logger对象
    """
    return _logger_manager.setup_logger(plan_name, log_directory)


def get_log_file_path() -> Optional[str]:
    """获取日志文件路径"""
    return _logger_manager.get_log_file_path()
