"""CPK计算器"""

from typing import List, Tuple, Optional
import numpy as np
from ..config.constants import D2_CONSTANT
from ..models.tolerance import Tolerance
from ..processors.resolution_processor import ResolutionProcessor


class CpkCalculator:
    """CPK计算器 - 使用组内标准差方法"""
    
    def __init__(self):
        self.resolution_processor = ResolutionProcessor()
    
    def calculate_cpk_excel_method(
        self,
        measurement_data: List[List[float]],
        tolerance: Tolerance,
        resolution: Optional[float]
    ) -> Tuple[float, float, float]:
        """
        使用组内标准差(Rbar/d2)的cpk计算方法
        
        Args:
            measurement_data: 测量数据矩阵 (5x25)
            tolerance: 公差信息
            resolution: 分辨率
            
        Returns:
            (cpk, rbar, sigma_within) 元组
        """
        try:
            # 获取所有125个原始数据
            all_data = []
            for col in range(25):  # 25个子组
                for row in range(5):  # 每个子组5个数据
                    all_data.append(measurement_data[row][col])
            
            # 应用分辨率舍入
            rounded_data = []
            for value in all_data:
                if value is not None:
                    rounded_value = self.resolution_processor.apply_resolution(value, resolution)
                    rounded_data.append(rounded_value)
                else:
                    rounded_data.append(value)
            
            # 计算平均值（对应Excel中的AVERAGE(C32:AA36)）
            avg = np.mean(rounded_data)
            
            # 计算每个子组的极差和平均极差Rbar
            r_values = []
            for col in range(25):
                # 获取每个子组的数据
                subgroup = []
                for row in range(5):
                    subgroup.append(rounded_data[col * 5 + row])
                
                # 计算子组极差
                r_val = max(subgroup) - min(subgroup)
                r_values.append(r_val)
            
            # 计算平均极差Rbar
            r_bar = np.mean(r_values) if r_values else 0
            
            # 计算组内标准差：Rbar / d2 (d2=2.326, n=5)
            sigma_within = r_bar / D2_CONSTANT if D2_CONSTANT > 0 else 0
            
            # 如果标准差为0或非常小，返回0
            if sigma_within == 0 or sigma_within < 1e-10:
                return 0.0, r_bar, sigma_within
            
            # 计算Ppu（使用组内标准差）
            if tolerance.usl is not None:
                ppu = abs(tolerance.usl - avg) / (3 * sigma_within)
            else:
                ppu = float('inf')
            
            # 计算Ppl（使用组内标准差）
            if tolerance.lsl is not None:
                ppl = abs(avg - tolerance.lsl) / (3 * sigma_within)
            else:
                ppl = float('inf')
            
            # 计算cpk - 根据单边/双边公差分别处理
            if tolerance.usl is not None and tolerance.lsl is not None:
                # 双边公差：取较小值
                cpk = min(ppu, ppl)
            elif tolerance.usl is not None:
                # 只有上公差：使用Ppu
                cpk = ppu
            elif tolerance.lsl is not None:
                # 只有下公差：使用Ppl
                cpk = ppl
            else:
                # 没有公差：无法计算cpk
                cpk = 0.0
            
            return cpk, r_bar, sigma_within
            
        except Exception as e:
            print(f"计算Excel方法cpk时出错: {e}")
            return 0.0, 0.0, 0.0
