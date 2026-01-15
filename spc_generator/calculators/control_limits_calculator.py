"""控制限计算器"""

from typing import Optional
from ..models.tolerance import Tolerance
from ..models.control_limits import ControlLimits
from ..config.constants import D2_CONSTANT, D3_CONSTANT, D4_CONSTANT
from ..utils.validation_utils import ValidationUtils


class ControlLimitsCalculator:
    """控制限计算器"""
    
    def __init__(self):
        self.validator = ValidationUtils()
    
    def calculate(
        self,
        tolerance: Tolerance,
        target_cpk: float = 1.8,
        ref_center: Optional[float] = None,
        subgroup_size: int = 5
    ) -> ControlLimits:
        """
        计算控制限
        
        Args:
            tolerance: 公差信息
            target_cpk: 目标CPK值
            ref_center: 参考中心（用于参考分布范围模式）
            subgroup_size: 子组大小
            
        Returns:
            ControlLimits对象
        """
        # 1. 确定中心线CL
        if ref_center is not None:
            cl = ref_center
        elif tolerance.usl is not None and tolerance.lsl is not None:
            cl = (tolerance.usl + tolerance.lsl) / 2
        elif tolerance.usl is not None:
            cl = tolerance.usl / 2
        elif tolerance.lsl is not None:
            cl = tolerance.lsl * 1.5
        else:
            cl = 0.0
        
        # 2. 计算公差范围
        if tolerance.usl is not None and tolerance.lsl is not None:
            tolerance_range = tolerance.usl - tolerance.lsl
        elif tolerance.usl is not None:
            tolerance_range = tolerance.usl
        else:
            tolerance_range = cl - (tolerance.lsl or 0.0)
        
        # 3. 基于目标CPK计算标准差
        sigma = tolerance_range / (6 * target_cpk) if target_cpk > 0 else 0.0
        
        # 4. 计算Xbar图控制限
        ucl = cl + 3 * sigma
        lcl = cl - 3 * sigma
        ucl1 = cl + sigma
        ucl2 = cl + 2 * sigma
        lcl1 = cl - sigma
        lcl2 = cl - 2 * sigma
        
        # 5. 计算R图控制限
        r_bar = sigma * D2_CONSTANT
        uclr = D4_CONSTANT * r_bar
        lclr = D3_CONSTANT * r_bar
        
        return ControlLimits(
            cl=self.validator.format_value(cl, 3),
            ucl=self.validator.format_value(ucl, 3),
            lcl=self.validator.format_value(lcl, 3),
            ucl1=self.validator.format_value(ucl1, 3),
            ucl2=self.validator.format_value(ucl2, 3),
            lcl1=self.validator.format_value(lcl1, 3),
            lcl2=self.validator.format_value(lcl2, 3),
            clr=self.validator.format_value(r_bar, 3),
            uclr=self.validator.format_value(uclr, 3),
            lclr=self.validator.format_value(lclr, 3),
            sigma=sigma,
            r_bar=r_bar
        )
    
    def validate_control_limits(self, limits: ControlLimits) -> bool:
        """验证控制限是否合理"""
        if limits.ucl <= limits.lcl:
            return False
        if limits.uclr <= limits.lclr:
            return False
        if limits.sigma <= 0:
            return False
        return True
