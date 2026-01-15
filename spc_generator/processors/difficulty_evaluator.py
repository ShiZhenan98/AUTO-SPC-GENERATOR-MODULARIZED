"""难度评估器"""

from typing import Tuple
from ..models.tolerance import Tolerance


class DifficultyEvaluator:
    """难度评估器"""
    
    def evaluate(
        self,
        tolerance: Tolerance,
        ref_lower: float,
        ref_upper: float,
        target_cpk: float
    ) -> Tuple[float, float, str]:
        """
        评估生成难度
        
        Args:
            tolerance: 公差信息
            ref_lower: 参考范围下限
            ref_upper: 参考范围上限
            target_cpk: 目标CPK
            
        Returns:
            (cpk下限, cpk上限, 难度评估)
        """
        ref_width = ref_upper - ref_lower
        ref_center = (ref_lower + ref_upper) / 2
        
        # 计算均匀分布（最分散）和正态分布（最集中）的标准差
        sigma_max = ref_width / 2.326  # 保守估计的标准差
        sigma_min = ref_width / 6      # 6个sigma在参考范围内
        
        if tolerance.usl is not None and tolerance.lsl is not None:
            # 双边公差
            ppu_max = (tolerance.usl - ref_center) / (3 * sigma_max)
            ppl_max = (ref_center - tolerance.lsl) / (3 * sigma_max)
            cpk_lower = min(ppu_max, ppl_max)
            
            ppu_min = (tolerance.usl - ref_center) / (3 * sigma_min)
            ppl_min = (ref_center - tolerance.lsl) / (3 * sigma_min)
            cpk_upper = min(ppu_min, ppl_min)
            
        elif tolerance.usl is not None:
            # 只有上公差
            cpk_lower = (tolerance.usl - ref_center) / (3 * sigma_max)
            cpk_upper = (tolerance.usl - ref_center) / (3 * sigma_min)
            
        elif tolerance.lsl is not None:
            # 只有下公差
            cpk_lower = (ref_center - tolerance.lsl) / (3 * sigma_max)
            cpk_upper = (ref_center - tolerance.lsl) / (3 * sigma_min)
        else:
            # 没有公差
            cpk_lower, cpk_upper = 0.0, 0.0
        
        # 评估难度
        difficulty = "中等"
        if cpk_lower > 2.0 or cpk_upper < 1.5:
            difficulty = "高"
        elif 1.7 <= cpk_lower <= 1.9 and 1.8 <= cpk_upper <= 2.2:
            difficulty = "低"
        
        return cpk_lower, cpk_upper, difficulty
