"""参考范围解析器"""

import re
from typing import Optional, Tuple
import pandas as pd
from ..utils.validation_utils import ValidationUtils


class ReferenceRangeParser:
    """参考分布范围解析器"""
    
    def __init__(self):
        self.validator = ValidationUtils()
    
    def parse(self, range_str: str) -> Tuple[Optional[float], Optional[float]]:
        """
        解析参考分布范围字符串，格式如'52.992-52.999'
        
        Args:
            range_str: 参考范围字符串
            
        Returns:
            (下限, 上限) 元组
        """
        if not range_str or pd.isna(range_str) or str(range_str).strip() == '':
            return None, None
        
        range_str = str(range_str).strip()
        
        # 移除可能的空格和特殊字符
        range_str = re.sub(r'\s+', '', range_str)
        
        # 匹配"数值-数值"格式
        pattern = r'^([-+]?\d*\.?\d+)\s*[-~–—]\s*([-+]?\d*\.?\d+)$'
        match = re.match(pattern, range_str)
        
        if not match:
            # 尝试其他可能的格式
            pattern2 = r'^([-+]?\d*\.?\d+)\s*[~]\s*([-+]?\d*\.?\d+)$'
            match = re.match(pattern2, range_str)
        
        if match:
            try:
                lower = self.validator.safe_float_convert(match.group(1))
                upper = self.validator.safe_float_convert(match.group(2))
                if lower is not None and upper is not None and lower < upper:
                    return lower, upper
            except:
                pass
        
        return None, None
