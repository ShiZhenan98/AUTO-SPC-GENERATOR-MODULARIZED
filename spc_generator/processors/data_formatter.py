"""数据格式化器"""

from typing import Optional
from ..utils.validation_utils import ValidationUtils


class DataFormatter:
    """数据格式化器"""
    
    def __init__(self):
        self.validator = ValidationUtils()
    
    def format_value(self, value: Optional[float], decimal_places: int = 3) -> float:
        """
        格式化数值到指定小数位
        
        Args:
            value: 待格式化的数值
            decimal_places: 小数位数
            
        Returns:
            格式化后的数值
        """
        return self.validator.format_value(value, decimal_places)
    
    def get_decimal_places(self, value: float) -> int:
        """获取数值的小数位数"""
        return self.validator.get_decimal_places(value)
