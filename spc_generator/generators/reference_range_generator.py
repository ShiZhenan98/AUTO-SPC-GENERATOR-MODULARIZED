"""参考范围模式生成器"""

import random
from typing import Optional, List, Tuple
import numpy as np
from .base_generator import BaseGenerator
from ..models.tolerance import Tolerance
from ..models.control_limits import ControlLimits
from ..models.spc_data import SPCData
from ..calculators.cpk_calculator import CpkCalculator
from ..calculators.eight_rules_checker import EightRulesChecker
from ..processors.resolution_processor import ResolutionProcessor
from ..processors.data_formatter import DataFormatter
from .standard_generator import StandardGenerator


class ReferenceRangeGenerator(BaseGenerator):
    """参考范围模式生成器 - 基于参考分布范围生成数据"""
    
    def __init__(self):
        self.cpk_calculator = CpkCalculator()
        self.rules_checker = EightRulesChecker()
        self.resolution_processor = ResolutionProcessor()
        self.formatter = DataFormatter()
        self.standard_generator = StandardGenerator()  # 复用标准生成器的辅助方法
    
    def generate(
        self,
        tolerance: Tolerance,
        control_limits: ControlLimits,
        target_cpk: float,
        resolution: Optional[float],
        max_attempts: int = 20000,
        ref_lower: Optional[float] = None,
        ref_upper: Optional[float] = None,
        **kwargs
    ) -> Optional[SPCData]:
        """
        参考范围模式生成SPC数据
        
        Args:
            tolerance: 公差信息
            control_limits: 控制限
            target_cpk: 目标CPK
            resolution: 分辨率
            max_attempts: 最大尝试次数
            ref_lower: 参考范围下限
            ref_upper: 参考范围上限
            
        Returns:
            SPCData对象，失败返回None
        """
        if ref_lower is None or ref_upper is None:
            return None
        
        print(f"    使用参考分布范围模式: {ref_lower:.4f} - {ref_upper:.4f}")
        
        # 检查参考范围是否超差
        if tolerance.usl is not None and ref_upper > tolerance.usl:
            print(f"    请检查参考分布范围是否超差: 上限{ref_upper} > 公差上限{tolerance.usl}")
            return None
        
        if tolerance.lsl is not None and ref_lower < tolerance.lsl:
            print(f"    请检查参考分布范围是否超差: 下限{ref_lower} < 公差下限{tolerance.lsl}")
            return None
        
        # 计算参考中心
        ref_center = (ref_lower + ref_upper) / 2
        ref_width = ref_upper - ref_lower
        
        decimal_places = 3
        best_result = None
        best_diff = float('inf')
        
        for attempt in range(max_attempts):
            try:
                # 生成X值，确保所有25个Xbar都在参考范围内
                x_values, _ = self._generate_x_values_with_reference_range(
                    ref_center, ref_lower, ref_upper, control_limits, decimal_places
                )
                
                # 检查Xbar是否全部在参考范围内
                xbar_all_in_range = all(ref_lower <= x <= ref_upper for x in x_values)
                if not xbar_all_in_range:
                    continue
                
                # 生成R值
                r_values = self.standard_generator._generate_natural_r_values(control_limits, decimal_places)
                
                # 生成详细的测量数据，要求每个子组至少4/5个点在参考范围内
                measurement_data = []
                for i in range(25):
                    subgroup = self._generate_subgroup_with_reference_requirement(
                        x_values[i], r_values[i], control_limits,
                        ref_lower, ref_upper, 5, decimal_places, min_points_in_range=4
                    )
                    measurement_data.append(subgroup)
                
                # 转置数据
                measurement_data = list(map(list, zip(*measurement_data)))
                
                # 应用分辨率舍入
                rounded_measurement_data = self.resolution_processor.apply_resolution_to_matrix(
                    measurement_data, resolution
                )
                
                # 计算原始数据在参考范围内的点数
                raw_in_range_count, total_raw_points = self._count_raw_data_in_reference_range(
                    rounded_measurement_data, ref_lower, ref_upper
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
                rounded_x_values, rounded_r_values = self.standard_generator._recalculate_x_r_values(
                    rounded_measurement_data
                )
                
                # 再次确认Xbar全部在参考范围内
                xbar_all_in_range_rounded = all(ref_lower <= x <= ref_upper for x in rounded_x_values)
                
                # 检查判异准则
                all_violations = self.rules_checker.check_all_rules(
                    rounded_x_values, rounded_r_values, control_limits
                )
                
                # 如果满足所有条件，使用这个数据
                target_min = target_cpk - 0.03
                target_max = target_cpk + 0.03
                
                if (xbar_all_in_range_rounded and
                    raw_in_range_count >= 100 and
                    target_min <= excel_cpk <= target_max and
                    len(all_violations) == 0):
                    
                    print(f"    生成完成，参考范围内原始数据点: {raw_in_range_count}/125, Xbar全部在参考范围内")
                    print(f"    cpk = {excel_cpk:.4f}, Rbar = {excel_rbar:.6f}, σ(组内) = {excel_sigma_within:.6f}")
                    
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
                if (xbar_all_in_range_rounded and
                    raw_in_range_count >= 100 and
                    len(all_violations) == 0):
                    diff = abs(excel_cpk - target_cpk)
                    if diff < best_diff:
                        best_diff = diff
                        best_cpk = excel_cpk
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
                if attempt % 500 == 0 and attempt > 0:
                    print(f"    尝试{attempt}次后仍在搜索...")
                continue
        
        # 检查是否找到了符合要求的数据
        if best_result:
            return best_result
        
        print(f"    警告: 未找到符合参考分布范围严格要求的数据")
        # 尝试标准模式作为后备
        print(f"    尝试使用标准模式生成...")
        
        # 调用标准生成器作为后备
        from .standard_generator import StandardGenerator
        standard_gen = StandardGenerator()
        fallback_result = standard_gen.generate(
            tolerance=tolerance,
            control_limits=control_limits,
            target_cpk=target_cpk,
            resolution=resolution,
            max_attempts=max_attempts // 2
        )
        
        if fallback_result:
            print(f"    使用标准模式成功生成数据")
            return fallback_result
        
        print(f"    标准模式也未能生成数据")
        return None
    
    def _generate_x_values_with_reference_range(
        self,
        ref_center: float,
        ref_lower: float,
        ref_upper: float,
        control_limits: ControlLimits,
        decimal_places: int = 3,
        center_offset_sigma: float = 0.2
    ) -> Tuple[List[float], float]:
        """生成基于参考分布范围的X值"""
        x_values = []
        ref_width = ref_upper - ref_lower
        sigma = control_limits.sigma
        offset_range = sigma * center_offset_sigma
        
        max_offset = min(offset_range, (ref_upper - ref_center), (ref_center - ref_lower))
        if max_offset > 0:
            offset = random.uniform(-max_offset, max_offset)
        else:
            offset = 0
        
        adjusted_center = ref_center + offset
        
        # 确保所有25个Xbar都在参考范围内
        for i in range(25):
            if ref_width > 0:
                std_dev = ref_width / 6.0
                x_val = random.gauss(adjusted_center, std_dev)
                x_val = max(ref_lower, min(ref_upper, x_val))
            else:
                x_val = adjusted_center
            
            x_val = self.formatter.format_value(x_val, decimal_places)
            x_values.append(x_val)
        
        return x_values, offset
    
    def _generate_subgroup_with_reference_requirement(
        self,
        x_mean: float,
        r_value: float,
        control_limits: ControlLimits,
        ref_lower: float,
        ref_upper: float,
        size: int = 5,
        decimal_places: int = 3,
        min_points_in_range: int = 4
    ) -> List[float]:
        """生成子组数据，要求子组内至少min_points_in_range个点在参考范围内"""
        max_attempts = 200
        
        for attempt in range(max_attempts):
            # 使用标准生成器的子组生成方法
            subgroup = self.standard_generator._generate_natural_subgroup_data(
                x_mean, r_value, control_limits, size, decimal_places, allow_variation=0.05
            )
            
            # 统计在参考范围内的点数
            in_range_count = sum(1 for val in subgroup if ref_lower <= val <= ref_upper)
            
            if in_range_count >= min_points_in_range:
                return subgroup
        
        # 如果多次尝试失败，强制调整
        return self._generate_forced_subgroup_with_reference(
            x_mean, r_value, control_limits, ref_lower, ref_upper, size, decimal_places, min_points_in_range
        )
    
    def _generate_forced_subgroup_with_reference(
        self,
        x_mean: float,
        r_value: float,
        control_limits: ControlLimits,
        ref_lower: float,
        ref_upper: float,
        size: int = 5,
        decimal_places: int = 3,
        min_points_in_range: int = 4
    ) -> List[float]:
        """强制生成满足参考范围要求的子组数据"""
        base_subgroup = self.standard_generator._generate_natural_subgroup_data(
            x_mean, r_value, control_limits, size, decimal_places
        )
        
        in_range_count = sum(1 for val in base_subgroup if ref_lower <= val <= ref_upper)
        
        if in_range_count >= min_points_in_range:
            return base_subgroup
        
        # 调整超出范围的点
        adjusted_subgroup = base_subgroup.copy()
        for i in range(len(adjusted_subgroup)):
            if not (ref_lower <= adjusted_subgroup[i] <= ref_upper):
                if adjusted_subgroup[i] > ref_upper:
                    adjusted_subgroup[i] = ref_upper - random.uniform(0, (ref_upper - ref_lower) * 0.1)
                else:
                    adjusted_subgroup[i] = ref_lower + random.uniform(0, (ref_upper - ref_lower) * 0.1)
                adjusted_subgroup[i] = self.formatter.format_value(adjusted_subgroup[i], decimal_places)
        
        # 重新计算平均值
        current_mean = np.mean(adjusted_subgroup)
        if abs(current_mean - x_mean) > (ref_upper - ref_lower) * 0.1:
            adjustment = x_mean - current_mean
            adjusted_subgroup = [
                self.formatter.format_value(val + adjustment, decimal_places)
                for val in adjusted_subgroup
            ]
        
        return adjusted_subgroup
    
    def _count_raw_data_in_reference_range(
        self,
        measurement_data: List[List[float]],
        ref_lower: float,
        ref_upper: float
    ) -> Tuple[int, int]:
        """计算125个原始数据中在参考范围内的点数"""
        count = 0
        total_points = 0
        
        for row in range(5):
            for col in range(25):
                value = measurement_data[row][col]
                if value is not None:
                    total_points += 1
                    if ref_lower <= value <= ref_upper:
                        count += 1
        
        return count, total_points
