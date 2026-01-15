"""SPC数据模型"""

from dataclasses import dataclass
from typing import List, Optional
import numpy as np


@dataclass
class SPCData:
    """SPC生成数据模型"""
    measurement_data: List[List[float]]      # 原始测量数据 (5x25)
    rounded_measurement_data: List[List[float]]  # 舍入后的测量数据 (5x25)
    x_values: List[float]                    # Xbar值 (25个)
    r_values: List[float]                    # R值 (25个)
    actual_cpk: float                        # 实际CPK
    rbar: float                              # 平均极差
    sigma_within: float                      # 组内标准差
    max_decimal_places: int                  # 最大小数位数
    control_limits: Optional[object] = None  # 控制限对象
    
    def get_x_values_array(self) -> np.ndarray:
        """获取X值数组"""
        return np.array(self.x_values)
    
    def get_r_values_array(self) -> np.ndarray:
        """获取R值数组"""
        return np.array(self.r_values)
    
    def get_measurement_matrix(self, rounded: bool = True) -> np.ndarray:
        """获取测量数据矩阵"""
        data = self.rounded_measurement_data if rounded else self.measurement_data
        return np.array(data)
