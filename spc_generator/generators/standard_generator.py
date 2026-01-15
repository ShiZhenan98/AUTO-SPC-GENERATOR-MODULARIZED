"""标准模式生成器"""

import random
from typing import Optional, List, Tuple
import numpy as np
from .base_generator import BaseGenerator
from ..models.tolerance import Tolerance
from ..models.control_limits import ControlLimits
from ..models.spc_data import SPCData
from ..calculators.control_limits_calculator import ControlLimitsCalculator
from ..calculators.cpk_calculator import CpkCalculator
from ..calculators.eight_rules_checker import EightRulesChecker
from ..processors.resolution_processor import ResolutionProcessor
from ..processors.data_formatter import DataFormatter


class StandardGenerator(BaseGenerator):
    """标准模式生成器 - 基于公差范围生成数据"""
    
    def __init__(self):
        self.calculator = ControlLimitsCalculator()
        self.cpk_calculator = CpkCalculator()
        self.rules_checker = EightRulesChecker()
        self.resolution_processor = ResolutionProcessor()
        self.formatter = DataFormatter()
    
    def generate(
        self,
        tolerance: Tolerance,
        control_limits: ControlLimits,
        target_cpk: float,
        resolution: Optional[float],
        max_attempts: int = 4000,
        **kwargs
    ) -> Optional[SPCData]:
        """
        标准模式生成SPC数据
        
        Args:
            tolerance: 公差信息
            control_limits: 控制限
            target_cpk: 目标CPK
            resolution: 分辨率
            max_attempts: 最大尝试次数
            
        Returns:
            SPCData对象，失败返回None
        """
        decimal_places = 3
        
        # 计算中心值
        center = tolerance.center or 0.0
        
        best_result = None
        best_diff = float('inf')
        
        for attempt in range(max_attempts):
            try:
                # 生成X值和R值
                x_values, _ = self._generate_natural_x_values(
                    center, control_limits, tolerance, decimal_places, center_offset_sigma=0.2
                )
                r_values = self._generate_natural_r_values(control_limits, decimal_places)
                
                # 生成详细的测量数据
                measurement_data = []
                for i in range(25):
                    subgroup = self._generate_natural_subgroup_data(
                        x_values[i], r_values[i], control_limits, 5, decimal_places, allow_variation=0.05
                    )
                    measurement_data.append(subgroup)
                
                # 转置数据
                measurement_data = list(map(list, zip(*measurement_data)))
                
                # 应用分辨率舍入
                rounded_measurement_data = self.resolution_processor.apply_resolution_to_matrix(
                    measurement_data, resolution
                )
                
                # 计算舍入后的数据的小数位数
                max_decimal_places = self.resolution_processor.calculate_max_decimal_places(
                    rounded_measurement_data
                )
                
                # 使用组内标准差计算方法计算cpk
                excel_cpk, excel_rbar, excel_sigma_within = self.cpk_calculator.calculate_cpk_excel_method(
                    rounded_measurement_data, tolerance, resolution
                )
                
                # 重新计算舍入后的x_values和r_values
                rounded_x_values, rounded_r_values = self._recalculate_x_r_values(rounded_measurement_data)
                
                # 使用八准则检查
                all_violations = self.rules_checker.check_all_rules(
                    rounded_x_values, rounded_r_values, control_limits
                )
                
                # 如果满足条件，使用这个数据
                target_min = target_cpk - 0.03
                target_max = target_cpk + 0.03
                
                if target_min <= excel_cpk <= target_max and len(all_violations) == 0:
                    return SPCData(
                        measurement_data=measurement_data,
                        rounded_measurement_data=rounded_measurement_data,
                        x_values=rounded_x_values,
                        r_values=rounded_r_values,
                        actual_cpk=excel_cpk,
                        rbar=excel_rbar,
                        sigma_within=excel_sigma_within,
                        max_decimal_places=max_decimal_places,
                        control_limits=control_limits
                    )
                
                # 记录最佳尝试
                if len(all_violations) == 0:
                    diff = abs(excel_cpk - target_cpk)
                    if diff < best_diff:
                        best_diff = diff
                        best_result = SPCData(
                            measurement_data=measurement_data,
                            rounded_measurement_data=rounded_measurement_data,
                            x_values=rounded_x_values,
                            r_values=rounded_r_values,
                            actual_cpk=excel_cpk,
                            rbar=excel_rbar,
                            sigma_within=excel_sigma_within,
                            max_decimal_places=max_decimal_places,
                            control_limits=control_limits
                        )
            
            except Exception:
                continue
        
        # 返回最佳结果
        if best_result:
            return best_result
        
        print(f"    警告: 未找到理想数据")
        return None
    
    def _generate_natural_x_values(
        self,
        center: float,
        control_limits: ControlLimits,
        tolerance: Tolerance,
        decimal_places: int = 3,
        center_offset_sigma: float = 0.25
    ) -> Tuple[List[float], float]:
        """生成自然的X值，允许中心在±sigma内浮动"""
        x_values = []
        sigma = control_limits.sigma
        offset_range = sigma * center_offset_sigma
        
        offset = random.uniform(-offset_range, offset_range)
        adjusted_center = center + offset
        
        safe_margin = (control_limits.ucl - control_limits.lcl) * 0.08
        safe_min = control_limits.lcl + safe_margin
        safe_max = control_limits.ucl - safe_margin
        
        if safe_min >= safe_max:
            safe_min = control_limits.lcl + (control_limits.ucl - control_limits.lcl) * 0.05
            safe_max = control_limits.ucl - (control_limits.ucl - control_limits.lcl) * 0.05
        
        for i in range(25):
            std_dev = sigma * 0.8
            x_val = random.gauss(adjusted_center, std_dev)
            x_val = max(safe_min, min(safe_max, x_val))
            x_val = self.formatter.format_value(x_val, decimal_places)
            
            if x_val >= control_limits.ucl or x_val <= control_limits.lcl:
                if x_val >= control_limits.ucl:
                    x_val = safe_max - (safe_max - safe_min) * 0.05
                else:
                    x_val = safe_min + (safe_max - safe_min) * 0.05
                x_val = self.formatter.format_value(x_val, decimal_places)
            
            x_values.append(x_val)
        
        return x_values, offset
    
    def _generate_natural_r_values(self, control_limits: ControlLimits, decimal_places: int = 3) -> List[float]:
        """生成自然的R值"""
        r_values = []
        target_r = control_limits.clr
        safe_max = control_limits.uclr * 0.95
        min_r = max(target_r * 0.15, 0.001)
        max_r = min(target_r * 1.2, safe_max)
        
        if min_r >= max_r:
            min_r = max(target_r * 0.15, 0.001)
            max_r = target_r * 1.1
        
        for i in range(25):
            r_val = random.uniform(min_r, max_r)
            r_val = self.formatter.format_value(r_val, decimal_places)
            
            if r_val == 0:
                r_val = min_r + (max_r - min_r) * 0.1
                r_val = self.formatter.format_value(r_val, decimal_places)
            
            if r_val >= control_limits.uclr:
                r_val = safe_max * 0.95
                r_val = self.formatter.format_value(r_val, decimal_places)
            
            r_values.append(r_val)
        
        return r_values
    
    def _generate_natural_subgroup_data(
        self,
        target_mean: float,
        range_val: float,
        control_limits: ControlLimits,
        size: int = 5,
        decimal_places: int = 3,
        allow_variation: float = 0.1
    ) -> List[float]:
        """生成自然的子组数据，允许实际平均值在目标平均值附近小范围波动"""
        max_attempts = 200
        
        for attempt in range(max_attempts):
            allowed_variation = abs(target_mean) * allow_variation if target_mean != 0 else range_val * 0.1
            min_mean = target_mean - allowed_variation
            max_mean = target_mean + allowed_variation
            
            min_range = max(range_val, 0.001)
            min_val = target_mean - min_range
            max_val = target_mean + min_range
            
            min_val = max(min_val, control_limits.lcl + 0.0005)
            max_val = min(max_val, control_limits.ucl - 0.0005)
            
            points = []
            for _ in range(size):
                point = random.uniform(min_val, max_val)
                point = max(control_limits.lcl + 0.0005, min(control_limits.ucl - 0.0005, point))
                points.append(point)
            
            current_mean = np.mean(points)
            
            if min_mean <= current_mean <= max_mean:
                pass
            else:
                if current_mean > max_mean:
                    adjustment = max_mean - current_mean
                else:
                    adjustment = min_mean - current_mean
                
                adjusted_points = []
                for p in points:
                    adjusted = p + adjustment
                    adjusted = max(control_limits.lcl + 0.0005, min(control_limits.ucl - 0.0005, adjusted))
                    adjusted_points.append(adjusted)
                
                points = adjusted_points
                current_mean = np.mean(points)
            
            all_in_control = all(control_limits.lcl <= p <= control_limits.ucl for p in points)
            range_non_zero = max(points) - min(points) > 0
            
            if all_in_control and range_non_zero:
                formatted_points = [self.formatter.format_value(p, decimal_places) for p in points]
                return formatted_points
        
        # 后备方法
        safe_points = []
        safe_range = max((control_limits.ucl - control_limits.lcl) * 0.15, 0.001)
        safe_min = target_mean - safe_range / 2
        safe_max = target_mean + safe_range / 2
        
        base_point = random.uniform(safe_min, safe_max)
        safe_points.append(self.formatter.format_value(base_point, decimal_places))
        
        for _ in range(size - 1):
            point = base_point + random.uniform(-safe_range/4, safe_range/4)
            point = max(safe_min, min(safe_max, point))
            safe_points.append(self.formatter.format_value(point, decimal_places))
        
        if max(safe_points) - min(safe_points) == 0:
            safe_points[-1] = self.formatter.format_value(safe_points[-1] + safe_range * 0.01, decimal_places)
        
        return safe_points
    
    def _recalculate_x_r_values(
        self, rounded_measurement_data: List[List[float]]
    ) -> Tuple[List[float], List[float]]:
        """重新计算舍入后的x_values和r_values"""
        rounded_x_values = []
        rounded_r_values = []
        
        for i in range(25):
            subgroup = [rounded_measurement_data[row_idx][i] for row_idx in range(5)]
            subgroup_avg = np.mean(subgroup)
            subgroup_range = max(subgroup) - min(subgroup)
            rounded_x_values.append(subgroup_avg)
            rounded_r_values.append(subgroup_range)
        
        return rounded_x_values, rounded_r_values
