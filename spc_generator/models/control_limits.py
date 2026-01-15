"""控制限数据模型"""

from dataclasses import dataclass


@dataclass
class ControlLimits:
    """控制限模型"""
    cl: float       # 中心线
    ucl: float      # 上控制限
    lcl: float      # 下控制限
    ucl1: float     # UCL-1σ
    ucl2: float     # UCL-2σ
    lcl1: float     # LCL+1σ
    lcl2: float     # LCL+2σ
    clr: float      # R图中心线
    uclr: float     # R图上控制限
    lclr: float     # R图下控制限
    sigma: float    # 标准差
    r_bar: float    # 平均极差
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'cl': self.cl,
            'ucl': self.ucl,
            'lcl': self.lcl,
            'ucl1': self.ucl1,
            'ucl2': self.ucl2,
            'lcl1': self.lcl1,
            'lcl2': self.lcl2,
            'clr': self.clr,
            'uclr': self.uclr,
            'lclr': self.lclr,
            'sigma': self.sigma,
            'r_bar': self.r_bar
        }
