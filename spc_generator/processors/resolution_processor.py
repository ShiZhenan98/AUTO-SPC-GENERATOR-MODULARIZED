"""分辨率处理器"""

import random
from typing import Optional, List
import numpy as np


class ResolutionProcessor:
    """分辨率处理器"""
    
    def apply_resolution(self, value: Optional[float], resolution: Optional[float]) -> Optional[float]:
        """
        根据量具分辨率对数值进行舍入处理
        
        Args:
            value: 原始数值
            resolution: 分辨率字符串，如"0.01"、"0.02"等
            
        Returns:
            舍入后的数值
        """
        if resolution is None or value is None:
            return value
        
        try:
            # 清理分辨率字符串
            if isinstance(resolution, str):
                resolution_str = resolution.strip()
            else:
                resolution_str = str(resolution)
            
            # 转换为浮点数
            resolution_float = float(resolution_str)
            
            # 情况1: 十进制分辨率 (0.1, 0.01, 0.001, 0.0001)
            if resolution_float in [0.1, 0.01, 0.001, 0.0001, 0.00001]:
                decimal_places = abs(int(np.log10(resolution_float)))
                rounded = round(value, decimal_places)
                return rounded
            
            # 情况2: 0.02分辨率 (特殊处理)
            elif resolution_float == 0.02:
                rounded = round(value, 2)
                second_decimal = int(rounded * 100) % 10
                
                # 如果是奇数，随机调整±0.01
                if second_decimal % 2 == 1:
                    if random.choice([True, False]):
                        adjusted = rounded + 0.01
                    else:
                        adjusted = rounded - 0.01
                    
                    if adjusted < 0:
                        adjusted = rounded + 0.01 if rounded >= 0 else 0.0
                    
                    return round(adjusted, 2)
                
                return rounded
            
            # 情况3: 其他分辨率
            else:
                if '.' in resolution_str:
                    decimal_places = len(resolution_str.split('.')[1])
                    return round(value, decimal_places)
                else:
                    return round(value, 0)
                    
        except Exception as e:
            print(f"分辨率处理警告: {e}, 使用原始值")
            return value
    
    def apply_resolution_to_matrix(
        self, 
        data_matrix: List[List[float]], 
        resolution: Optional[float]
    ) -> List[List[float]]:
        """
        将分辨率舍入应用到整个数据矩阵
        
        Args:
            data_matrix: 数据矩阵
            resolution: 分辨率
            
        Returns:
            舍入后的数据矩阵
        """
        if not data_matrix or resolution is None:
            return data_matrix
        
        rounded_matrix = []
        for row in data_matrix:
            rounded_row = [self.apply_resolution(val, resolution) for val in row]
            rounded_matrix.append(rounded_row)
        
        return rounded_matrix
    
    def calculate_max_decimal_places(self, data_matrix: List[List[float]]) -> int:
        """计算数据矩阵中的最大小数位数"""
        max_decimal = 0
        for row in data_matrix:
            for value in row:
                if value is not None:
                    str_value = str(value)
                    if '.' in str_value:
                        decimal_places = len(str_value.split('.')[1])
                        max_decimal = max(max_decimal, decimal_places)
        return max_decimal
