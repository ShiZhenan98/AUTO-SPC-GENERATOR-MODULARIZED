"""生成器基类"""

from abc import ABC, abstractmethod
from typing import Optional
from ..models.tolerance import Tolerance
from ..models.control_limits import ControlLimits
from ..models.spc_data import SPCData


class BaseGenerator(ABC):
    """数据生成器基类"""
    
    @abstractmethod
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
        生成SPC数据
        
        Args:
            tolerance: 公差信息
            control_limits: 控制限
            target_cpk: 目标CPK
            resolution: 分辨率
            max_attempts: 最大尝试次数
            **kwargs: 其他参数
            
        Returns:
            SPCData对象，失败返回None
        """
        pass
