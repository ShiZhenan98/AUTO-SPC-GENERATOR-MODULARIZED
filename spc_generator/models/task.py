"""任务数据模型"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Task:
    """SPC任务数据模型"""
    row_index: int
    product_model: str
    process: str
    theory: str
    reference_range: Optional[str] = None
    inspection_item: str = ""
    resolution: Optional[float] = None
    equipment_no: str = ""
    target_cpk: float = 1.8
    month_status: Dict[str, bool] = field(default_factory=dict)
    
    def has_month(self, month_name: str) -> bool:
        """检查是否有该月份的任务"""
        return self.month_status.get(month_name, False)
