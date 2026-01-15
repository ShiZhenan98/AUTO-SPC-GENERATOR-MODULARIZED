"""验证工具"""

import re
from typing import Optional


class ValidationUtils:
    """验证工具类"""
    
    @staticmethod
    def safe_float_convert(value) -> Optional[float]:
        """
        安全地将字符串转换为浮点数
        
        Args:
            value: 待转换的值
            
        Returns:
            转换后的浮点数，失败返回None
        """
        if not value:
            return None
        
        if isinstance(value, str) and value.strip().upper() in ['OK', '/', '符合']:
            return None  # 特殊值不转换为浮点数
        
        if isinstance(value, (int, float)):
            return float(value)
        
        value_str = str(value)
        
        if value_str.startswith('='):
            return None  # Excel公式
        
        # 检查是否是包含换行符的多值情况
        if '\n' in value_str:
            parts = value_str.split('\n')
            for part in parts:
                part = part.strip()
                if part and any(char.isdigit() for char in part):
                    cleaned = re.sub(r'[^\d.-]', '', part)
                    if cleaned:
                        try:
                            return float(cleaned)
                        except ValueError:
                            continue
            return None
        
        if not any(char.isdigit() for char in value_str):
            return None
        
        cleaned = re.sub(r'[^\d.-]', '', value_str)
        
        if not cleaned:
            return None
        
        if cleaned.count('.') > 1:
            parts = cleaned.split('.')
            cleaned = parts[0] + '.' + ''.join(parts[1:])
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    @staticmethod
    def is_valid_name(text: str) -> bool:
        """
        验证文本是否看起来像有效的姓名
        
        Args:
            text: 待验证的文本
            
        Returns:
            是否为有效姓名
        """
        if not text:
            return False
        
        text = str(text).strip()
        
        # 检查长度（中文姓名通常2-4个字符）
        if len(text) < 2 or len(text) > 10:
            return False
        
        # 检查是否包含明显不是姓名的字符
        if re.search(r'[\d=+*/\\|\[\]{}]', text):
            return False
        
        # 检查是否看起来像公式或代码
        if text.startswith('=') or text.startswith('@'):
            return False
        
        # 对于中文姓名，检查是否包含中文字符
        if re.search(r'[\u4e00-\u9fff]', text):
            return True
        
        # 对于英文姓名，检查是否只包含字母和空格
        if re.match(r'^[A-Za-z\s]+$', text):
            return True
        
        return False
    
    @staticmethod
    def format_value(value: Optional[float], decimal_places: int = 3) -> float:
        """
        格式化数值到指定小数位
        
        Args:
            value: 待格式化的数值
            decimal_places: 小数位数
            
        Returns:
            格式化后的数值
        """
        import decimal
        
        if value is None:
            return 0.0
        
        if decimal_places == 0:
            return round(value)
        else:
            with decimal.localcontext() as ctx:
                ctx.rounding = decimal.ROUND_HALF_UP
                d = decimal.Decimal(str(value))
                rounded = round(d, decimal_places)
                return float(rounded)
    
    @staticmethod
    def get_decimal_places(value: float) -> int:
        """
        获取数值的小数位数
        
        Args:
            value: 数值
            
        Returns:
            小数位数
        """
        if value is None:
            return 0
        
        str_value = str(value)
        if '.' in str_value:
            return len(str_value.split('.')[1])
        return 0
