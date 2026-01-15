"""公差数据模型"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ToleranceType(Enum):
    """公差类型枚举"""
    DOUBLE = "double"      # 双边公差
    UPPER_ONLY = "upper"   # 只有上公差
    LOWER_ONLY = "lower"   # 只有下公差
    NONE = "none"          # 无公差


@dataclass
class Tolerance:
    """公差信息模型"""
    usl: Optional[float]           # 上规格限 (Upper Specification Limit)
    lsl: Optional[float]           # 下规格限 (Lower Specification Limit)
    tolerance_type: ToleranceType  # 公差类型
    raw_string: str                # 原始字符串
    
    @property
    def center(self) -> Optional[float]:
        """计算公差中心"""
        if self.usl is not None and self.lsl is not None:
            return (self.usl + self.lsl) / 2
        elif self.usl is not None:
            return self.usl / 2
        elif self.lsl is not None:
            return self.lsl * 1.5
        return None
    
    @property
    def width(self) -> Optional[float]:
        """计算公差范围"""
        if self.usl is not None and self.lsl is not None:
            return self.usl - self.lsl
        return None
    
    def is_valid(self) -> bool:
        """验证公差是否有效"""
        if self.tolerance_type == ToleranceType.DOUBLE:
            return self.usl is not None and self.lsl is not None and self.usl > self.lsl
        elif self.tolerance_type == ToleranceType.UPPER_ONLY:
            return self.usl is not None
        elif self.tolerance_type == ToleranceType.LOWER_ONLY:
            return self.lsl is not None
        return True
