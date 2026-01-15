"""文件工具"""

import os
import sys
import re
from pathlib import Path
from typing import Optional, List, Tuple


class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def get_script_directory() -> str:
        """获取脚本所在的目录（主脚本目录，而非工具模块目录）"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            # 获取主脚本的目录
            # 如果是从 run_spc_generator.py 运行，获取其目录
            # 如果是从 spc_generator.main 运行，获取其父目录
            main_module = sys.modules.get('__main__')
            if main_module and hasattr(main_module, '__file__'):
                main_file = main_module.__file__
                if main_file:
                    return os.path.dirname(os.path.abspath(main_file))
            
            # 如果无法获取主模块，尝试从调用栈获取
            import inspect
            frame = inspect.currentframe()
            try:
                # 向上查找调用栈，找到不在 spc_generator 包内的文件
                while frame:
                    filename = frame.f_globals.get('__file__', '')
                    if filename and 'spc_generator' not in filename.replace(os.sep, '/'):
                        return os.path.dirname(os.path.abspath(filename))
                    frame = frame.f_back
            finally:
                del frame
            
            # 最后回退：返回当前工作目录的父目录（假设在 spc_generator 子目录中）
            cwd = os.getcwd()
            if 'spc_generator' in cwd:
                # 如果在 spc_generator 子目录中，返回父目录
                return os.path.dirname(cwd)
            return cwd
    
    @staticmethod
    def set_working_directory(directory: Optional[str] = None) -> str:
        """设置工作目录"""
        if directory is None:
            directory = FileUtils.get_script_directory()
        os.chdir(directory)
        return directory
    
    @staticmethod
    def find_file(pattern: str, directory: str = ".") -> Optional[str]:
        """
        查找匹配模式的文件
        
        Args:
            pattern: 文件名模式（包含关键词）
            directory: 搜索目录
            
        Returns:
            找到的文件路径，未找到返回None
        """
        files = os.listdir(directory)
        matches = [f for f in files if pattern.lower() in f.lower() and f.endswith('.xlsx')]
        return matches[0] if matches else None
    
    @staticmethod
    def find_spc_plan_file(directory: str = ".") -> Optional[str]:
        """查找SPC推进计划文件"""
        files = os.listdir(directory)
        # 查找SPC推进计划文件
        spc_plan_files = [f for f in files if 'spc推进计划' in f.lower() and f.endswith('.xlsx')]
        if not spc_plan_files:
            spc_plan_files = [f for f in files if '推进计划' in f.lower() and f.endswith('.xlsx')]
        return spc_plan_files[0] if spc_plan_files else None
    
    @staticmethod
    def find_spc_template_file(directory: str = ".") -> Optional[str]:
        """查找SPC模板文件"""
        files = os.listdir(directory)
        spc_template_files = [f for f in files if 'spc模板' in f.lower() and f.endswith('.xlsx')]
        return spc_template_files[0] if spc_template_files else None
    
    @staticmethod
    def extract_workshop_name_and_year(filename: str) -> Tuple[str, int]:
        """
        从文件名中提取车间名称和年份
        
        Args:
            filename: 文件名，如"2025年SPC推进计划--VT.xlsx"
            
        Returns:
            (车间名称, 年份)
        """
        workshop_name = "车间"
        year = 2026
        
        # 提取年份
        year_match = re.search(r'(\d{4})年', filename)
        if year_match:
            year = int(year_match.group(1))
        
        # 提取车间名称
        match = re.search(r'--(\w+)\.', filename)
        if match:
            workshop_name = match.group(1)
        else:
            name_parts = filename.split('--')
            if len(name_parts) > 1:
                workshop_part = name_parts[-1].replace('.xlsx', '').replace('.xls', '')
                workshop_name = workshop_part
        
        return workshop_name, year
    
    @staticmethod
    def sanitize_filename(text: str, max_length: int = 50) -> str:
        """
        清理文件名，移除非法字符
        
        Args:
            text: 原始文本
            max_length: 最大长度
            
        Returns:
            清理后的文件名
        """
        # 移除非法字符
        safe_text = re.sub(r'[\\/*?:"<>|]', '', str(text))
        # 限制长度
        if len(safe_text) > max_length:
            safe_text = safe_text[:max_length]
        return safe_text
    
    @staticmethod
    def ensure_unique_filename(base_filename: str, directory: str = ".") -> str:
        """
        确保文件名唯一（如果存在则添加序号）
        
        Args:
            base_filename: 基础文件名
            directory: 目录路径
            
        Returns:
            唯一的文件名
        """
        if not os.path.exists(os.path.join(directory, base_filename)):
            return base_filename
        
        base_name, ext = os.path.splitext(base_filename)
        counter = 1
        while os.path.exists(os.path.join(directory, f"{base_name}_{counter}{ext}")):
            counter += 1
        
        return f"{base_name}_{counter}{ext}"
