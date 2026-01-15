"""理论值解析器 - 支持25+种公差格式"""

import re
from typing import Optional
import pandas as pd
from ..models.tolerance import Tolerance, ToleranceType
from ..utils.validation_utils import ValidationUtils


class TheoreticalValueParser:
    """理论值解析器 - 支持25+种公差格式"""
    
    def __init__(self):
        self.validator = ValidationUtils()
        # 解析策略列表（按优先级排序）
        self._strategies = [
            self._parse_special_values,
            self._parse_base_limit_format,
            self._parse_base_limit_variant,
            self._parse_limit_only,
            self._parse_multi_feature,
            self._parse_geometric_tolerance,
            self._parse_geometric_inequality,
            self._parse_roughness_inequality,
            self._parse_unit_numeric,
            self._parse_inequality,
            self._parse_roughness,
            self._parse_range_format,
            self._parse_asymmetric_tolerance,
            self._parse_symmetric_tolerance,
            self._parse_angle_tolerance,
            self._parse_chamfer_tolerance,
            self._parse_chamfer_max,
            self._parse_radius_tolerance,
            self._parse_min_tolerance,
            self._parse_max_tolerance,
            self._parse_thread_spec,
            self._parse_appearance_check,
            self._parse_material_spec,
            self._parse_simple_range,
            self._parse_simple_numeric,
        ]
        # 缓存
        self._cache = {}
    
    def parse(self, theory_str: str, use_cache: bool = True) -> Tolerance:
        """
        解析理论值字符串
        
        Args:
            theory_str: 理论值字符串
            use_cache: 是否使用缓存
            
        Returns:
            Tolerance对象
        """
        if not theory_str or pd.isna(theory_str) or str(theory_str).strip() == '':
            return Tolerance(None, None, ToleranceType.NONE, '')
        
        theory_str = str(theory_str).strip()
        
        # 检查缓存
        if use_cache and theory_str in self._cache:
            return self._cache[theory_str]
        
        # 尝试每种解析策略
        for strategy in self._strategies:
            result = strategy(theory_str)
            if result is not None:
                if use_cache:
                    self._cache[theory_str] = result
                return result
        
        # 无法解析，返回默认值
        print(f"警告: 无法解析理论值 '{theory_str}'，使用默认值")
        default = Tolerance(1.0, 0.0, ToleranceType.UPPER_ONLY, theory_str)
        if use_cache:
            self._cache[theory_str] = default
        return default
    
    # 1. 处理特殊值
    def _parse_special_values(self, text: str) -> Optional[Tolerance]:
        """解析特殊值：OK、/、符合"""
        if text.upper() in ['OK', '/', '符合']:
            return Tolerance(None, None, ToleranceType.NONE, text)
        return None
    
    # 2. 处理基值-下限-上限格式
    def _parse_base_limit_format(self, text: str) -> Optional[Tolerance]:
        """解析：基值:30.0；下限：29.947；上限：29.98"""
        match = re.search(r'基值\s*[:：]\s*([0-9.]+)\s*[;；]\s*下限\s*[:：]\s*([0-9.]+)\s*[;；]\s*上限\s*[:：]\s*([0-9.]+)', text)
        if match:
            lower_limit = self.validator.safe_float_convert(match.group(2))
            upper_limit = self.validator.safe_float_convert(match.group(3))
            if lower_limit is not None and upper_limit is not None:
                return Tolerance(upper_limit, lower_limit, ToleranceType.DOUBLE, text)
        return None
    
    # 3. 处理基值-下限-上限变体格式
    def _parse_base_limit_variant(self, text: str) -> Optional[Tolerance]:
        """解析：30.0；下限：29.947；上限：29.98"""
        match = re.search(r'([0-9.]+)\s*[;；]\s*下限\s*[:：]\s*([0-9.]+)\s*[;；]\s*上限\s*[:：]\s*([0-9.]+)', text)
        if match:
            lower_limit = self.validator.safe_float_convert(match.group(2))
            upper_limit = self.validator.safe_float_convert(match.group(3))
            if lower_limit is not None and upper_limit is not None:
                return Tolerance(upper_limit, lower_limit, ToleranceType.DOUBLE, text)
        return None
    
    # 4. 处理下限-上限格式
    def _parse_limit_only(self, text: str) -> Optional[Tolerance]:
        """解析：下限：29.947；上限：29.98"""
        match = re.search(r'下限\s*[:：]\s*([0-9.]+)\s*[;；]\s*上限\s*[:：]\s*([0-9.]+)', text)
        if match:
            lower_limit = self.validator.safe_float_convert(match.group(1))
            upper_limit = self.validator.safe_float_convert(match.group(2))
            if lower_limit is not None and upper_limit is not None:
                return Tolerance(upper_limit, lower_limit, ToleranceType.DOUBLE, text)
        return None
    
    # 5. 处理多特征格式
    def _parse_multi_feature(self, text: str) -> Optional[Tolerance]:
        """解析：2-φ3.5±0.1、2-120°±3°"""
        match = re.match(r'^\s*(\d+)\s*-\s*(.+)$', text)
        if match:
            real_spec = match.group(2).strip()
            # 递归解析真实的公差部分
            return self.parse(real_spec, use_cache=False)
        return None
    
    # 6. 优先处理形位公差
    def _parse_geometric_tolerance(self, text: str) -> Optional[Tolerance]:
        """解析：≤Φ0.04, Φ0.04, φ0.025"""
        match = re.match(r'^\s*[≤≥＜＞<>]?\s*[φΦ]\s*([0-9.]+)\s*$', text)
        if match:
            value = self.validator.safe_float_convert(match.group(1))
            if value is not None:
                return Tolerance(value, None, ToleranceType.UPPER_ONLY, text)
        return None
    
    # 7. 处理带比较符号的形位公差
    def _parse_geometric_inequality(self, text: str) -> Optional[Tolerance]:
        """解析：≤φ0.01"""
        match = re.match(r'^\s*[≤＜<]\s*[φΦ]?\s*([0-9.]+)\s*$', text)
        if match:
            value = self.validator.safe_float_convert(match.group(1))
            if value is not None:
                return Tolerance(value, None, ToleranceType.UPPER_ONLY, text)
        return None
    
    # 8. 处理带粗糙度符号和比较符号的格式
    def _parse_roughness_inequality(self, text: str) -> Optional[Tolerance]:
        """解析：≤Pt3.2, ≤Ra0.8, ≤Ry6.3, ≤Rpk0.2"""
        match = re.match(r'^\s*[≤＜<]\s*(Ra|Rz|Pt|Pa|Ry|Rpk)\s*([0-9.]+)\s*$', text, re.IGNORECASE)
        if match:
            value = self.validator.safe_float_convert(match.group(2))
            if value is not None:
                return Tolerance(value, None, ToleranceType.UPPER_ONLY, text)
        return None
    
    # 9. 处理带单位的简单数值公差
    def _parse_unit_numeric(self, text: str) -> Optional[Tolerance]:
        """解析：0.025mm"""
        match = re.match(r'^\s*([0-9.]+)\s*(mm|μm|°|度)?\s*$', text, re.IGNORECASE)
        if match:
            value = self.validator.safe_float_convert(match.group(1))
            if value is not None:
                return Tolerance(value, None, ToleranceType.UPPER_ONLY, text)
        return None
    
    # 10. 处理带比较符号的公差
    def _parse_inequality(self, text: str) -> Optional[Tolerance]:
        """解析：≤0.8, ＜0.025"""
        match = re.match(r'^\s*[≤＜<]\s*([0-9.]+)\s*$', text)
        if match:
            value = self.validator.safe_float_convert(match.group(1))
            if value is not None:
                return Tolerance(value, None, ToleranceType.UPPER_ONLY, text)
        return None
    
    # 11. 粗糙度公差格式
    def _parse_roughness(self, text: str) -> Optional[Tolerance]:
        """解析：Ra0.8, Pt3.2, Ry6.3, Rpk0.2"""
        match = re.match(r'^\s*(Ra|Rz|Pt|Pa|Ry|Rpk)\s*([0-9.]+)\s*$', text, re.IGNORECASE)
        if match:
            value = self.validator.safe_float_convert(match.group(2))
            if value is not None:
                return Tolerance(value, None, ToleranceType.UPPER_ONLY, text)
        return None
    
    # 12. 范围公差格式
    def _parse_range_format(self, text: str) -> Optional[Tolerance]:
        """解析：47.322-47.331 或 57.67-57.70"""
        if '-' in text:
            range_match = re.findall(r'[φ]?\s*([0-9.]+)\s*-\s*[φ]?\s*([0-9.]+)', text)
            if range_match:
                if re.match(r'^\s*[φ]?\s*[0-9.]+\s*-\s*[φ]?\s*[0-9.]+$', text):
                    min_val = self.validator.safe_float_convert(range_match[0][0])
                    max_val = self.validator.safe_float_convert(range_match[0][1])
                    if min_val and max_val:
                        return Tolerance(max_val, min_val, ToleranceType.DOUBLE, text)
        return None
    
    # 13. 不对称公差格式
    def _parse_asymmetric_tolerance(self, text: str) -> Optional[Tolerance]:
        """解析：27.4（-0.05/-0.1）"""
        match = re.match(r'^\s*[φ]?\s*([0-9.]+)\s*[（(]\s*([+-]?[0-9.]+)\s*/\s*([+-]?[0-9.]+)\s*[）)]\s*$', text)
        if match:
            base_value = self.validator.safe_float_convert(match.group(1))
            upper_tol = self.validator.safe_float_convert(match.group(2))
            lower_tol = self.validator.safe_float_convert(match.group(3))
            if base_value is not None and upper_tol is not None and lower_tol is not None:
                usl = base_value + upper_tol
                lsl = base_value + lower_tol
                return Tolerance(usl, lsl, ToleranceType.DOUBLE, text)
        return None
    
    # 14. 对称公差格式
    def _parse_symmetric_tolerance(self, text: str) -> Optional[Tolerance]:
        """解析：φ3.5±0.1"""
        match = re.match(r'^\s*[φ]?\s*([0-9.]+)\s*[°]?\s*[（(]?\s*±\s*([0-9.]+)\s*[°]?[）)]?\s*$', text)
        if match:
            base_value = self.validator.safe_float_convert(match.group(1))
            tolerance = self.validator.safe_float_convert(match.group(2))
            if base_value is not None and tolerance is not None:
                usl = base_value + tolerance
                lsl = base_value - tolerance
                return Tolerance(usl, lsl, ToleranceType.DOUBLE, text)
        return None
    
    # 15. 角度公差
    def _parse_angle_tolerance(self, text: str) -> Optional[Tolerance]:
        """解析：120°±3°"""
        match = re.match(r'([0-9.]+)\s*°\s*±\s*([0-9.]+)\s*°', text)
        if match:
            base_value = self.validator.safe_float_convert(match.group(1))
            tolerance = self.validator.safe_float_convert(match.group(2))
            if base_value is not None and tolerance is not None:
                usl = base_value + tolerance
                lsl = base_value - tolerance
                return Tolerance(usl, lsl, ToleranceType.DOUBLE, text)
        return None
    
    # 16. 倒角公差格式
    def _parse_chamfer_tolerance(self, text: str) -> Optional[Tolerance]:
        """解析：C0.3±0.2"""
        match = re.match(r'C\s*([0-9.]+)\s*±\s*([0-9.]+)', text)
        if match:
            base_value = self.validator.safe_float_convert(match.group(1))
            tolerance = self.validator.safe_float_convert(match.group(2))
            if base_value and tolerance:
                usl = base_value + tolerance
                lsl = base_value - tolerance
                return Tolerance(usl, lsl, ToleranceType.DOUBLE, text)
        return None
    
    # 17. 倒角最大值格式
    def _parse_chamfer_max(self, text: str) -> Optional[Tolerance]:
        """解析：C0.3max"""
        match = re.match(r'C\s*([0-9.]+)\s*max', text, re.IGNORECASE)
        if match:
            value = self.validator.safe_float_convert(match.group(1))
            if value is not None:
                return Tolerance(value, 0.0, ToleranceType.UPPER_ONLY, text)
        return None
    
    # 18. 圆角公差
    def _parse_radius_tolerance(self, text: str) -> Optional[Tolerance]:
        """解析：R1.5±0.3"""
        match = re.match(r'R\s*([0-9.]+)\s*±\s*([0-9.]+)', text)
        if match:
            base_value = self.validator.safe_float_convert(match.group(1))
            tolerance = self.validator.safe_float_convert(match.group(2))
            if base_value is not None and tolerance is not None:
                usl = base_value + tolerance
                lsl = base_value - tolerance
                return Tolerance(usl, lsl, ToleranceType.DOUBLE, text)
        return None
    
    # 19. 最小值公差
    def _parse_min_tolerance(self, text: str) -> Optional[Tolerance]:
        """解析：min25"""
        match = re.match(r'^min\s*([0-9.]+)$', text, re.IGNORECASE)
        if match:
            value = self.validator.safe_float_convert(match.group(1))
            if value is not None:
                return Tolerance(None, value, ToleranceType.LOWER_ONLY, text)
        return None
    
    # 20. 最大值公差
    def _parse_max_tolerance(self, text: str) -> Optional[Tolerance]:
        """解析：max50"""
        match = re.match(r'^max\s*([0-9.]+)$', text, re.IGNORECASE)
        if match:
            value = self.validator.safe_float_convert(match.group(1))
            if value is not None:
                return Tolerance(value, 0.0, ToleranceType.UPPER_ONLY, text)
        return None
    
    # 21. 螺纹规格
    def _parse_thread_spec(self, text: str) -> Optional[Tolerance]:
        """解析：M8"""
        match = re.match(r'[M]\d+', text)
        if match:
            return Tolerance(None, None, ToleranceType.NONE, text)
        return None
    
    # 22. 外观检查
    def _parse_appearance_check(self, text: str) -> Optional[Tolerance]:
        """解析：无锈蚀、缺陷、毛刺等"""
        keywords = ['无锈蚀', '缺陷', '毛刺', '锈蚀', '磕碰', '划伤', '不允许', '毛刺、裂纹、碰伤、锈蚀']
        if any(keyword in text for keyword in keywords):
            return Tolerance(None, None, ToleranceType.NONE, text)
        return None
    
    # 23. 材料规格
    def _parse_material_spec(self, text: str) -> Optional[Tolerance]:
        """解析：CrMo、GB/T"""
        keywords = ['CrMo', 'GB/T']
        if any(keyword in text for keyword in keywords):
            return Tolerance(None, None, ToleranceType.NONE, text)
        return None
    
    # 24. 尝试解析简单的双边公差
    def _parse_simple_range(self, text: str) -> Optional[Tolerance]:
        """解析：简单范围格式"""
        if '-' in text:
            parts = text.split('-')
            if len(parts) == 2:
                try:
                    lsl = float(parts[0].strip())
                    usl = float(parts[1].strip())
                    return Tolerance(usl, lsl, ToleranceType.DOUBLE, text)
                except:
                    pass
        return None
    
    # 25. 尝试解析单边公差
    def _parse_simple_numeric(self, text: str) -> Optional[Tolerance]:
        """解析：单边数值，如 0.075"""
        try:
            value = float(text)
            return Tolerance(value, 0.0, ToleranceType.UPPER_ONLY, text)
        except:
            pass
        return None
