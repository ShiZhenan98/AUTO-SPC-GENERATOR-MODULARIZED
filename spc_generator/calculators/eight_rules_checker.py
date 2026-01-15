"""8条判异准则检查器"""

from typing import List
from ..models.control_limits import ControlLimits


class EightRulesChecker:
    """8条判异准则检查器"""
    
    def check_all_rules(
        self,
        x_values: List[float],
        r_values: List[float],
        control_limits: ControlLimits
    ) -> List[str]:
        """
        检查全部的8个判异准则
        
        Args:
            x_values: Xbar值列表（25个）
            r_values: R值列表（25个）
            control_limits: 控制限对象
            
        Returns:
            违规列表
        """
        violations = []
        n = len(x_values)
        
        if n < 25:
            violations.append("数据点不足25个")
            return violations
        
        cl = control_limits.cl
        ucl = control_limits.ucl
        lcl = control_limits.lcl
        ucl1 = control_limits.ucl1
        lcl1 = control_limits.lcl1
        ucl2 = control_limits.ucl2
        lcl2 = control_limits.lcl2
        
        # 计算各区域边界
        A_upper = ucl
        A_lower = lcl
        B_upper = ucl2
        B_lower = lcl2
        C_upper = ucl1
        C_lower = lcl1
        
        # 准则1: 一点落在A区外
        violations.extend(self._check_rule_1(x_values, A_upper, A_lower))
        
        # 准则2: 连续6点递增或递减
        violations.extend(self._check_rule_2(x_values, n))
        
        # 准则3: 连续14点中相邻点上下交替
        violations.extend(self._check_rule_3(x_values, n))
        
        # 准则4: 连续15点落中心线两侧的C区内
        violations.extend(self._check_rule_4(x_values, n, C_lower, C_upper))
        
        # 准则5: 连续8点落在中心两侧且无一在C区内
        violations.extend(self._check_rule_5(x_values, n, cl, C_lower, C_upper))
        
        # 准则6: 连续9点落在中心线同一侧
        violations.extend(self._check_rule_6(x_values, n, cl))
        
        # 准则7: 连续3点中有2点落在中心线同一侧的B区以外
        violations.extend(self._check_rule_7(x_values, n, B_upper, B_lower))
        
        # 准则8: 连续5点中有4点落在中心同一侧的C区以外
        violations.extend(self._check_rule_8(x_values, n, C_upper, C_lower))
        
        # 检查R图
        violations.extend(self._check_r_chart(r_values, control_limits.uclr, control_limits.lclr))
        
        return violations
    
    def _check_rule_1(self, x_values: List[float], A_upper: float, A_lower: float) -> List[str]:
        """准则1: 一点落在A区外"""
        violations = []
        for i, x in enumerate(x_values):
            if x > A_upper or x < A_lower:
                violations.append(f"准则1: 第{i+1}点落在A区外")
        return violations
    
    def _check_rule_2(self, x_values: List[float], n: int) -> List[str]:
        """准则2: 连续6点递增或递减"""
        violations = []
        if n >= 6:
            for i in range(n - 5):
                increasing = all(x_values[i+j] < x_values[i+j+1] for j in range(5))
                decreasing = all(x_values[i+j] > x_values[i+j+1] for j in range(5))
                
                if increasing:
                    violations.append(f"准则2: 第{i+1}-{i+6}点连续递增")
                if decreasing:
                    violations.append(f"准则2: 第{i+1}-{i+6}点连续递减")
        return violations
    
    def _check_rule_3(self, x_values: List[float], n: int) -> List[str]:
        """准则3: 连续14点中相邻点上下交替"""
        violations = []
        if n >= 14:
            for i in range(n - 13):
                alternating = True
                for j in range(13):
                    diff1 = x_values[i+j] - x_values[i+j+1]
                    if j % 2 == 0:
                        if diff1 >= 0:
                            alternating = False
                            break
                    else:
                        if diff1 <= 0:
                            alternating = False
                            break
                
                if alternating:
                    violations.append(f"准则3: 第{i+1}-{i+14}点相邻点上下交替")
        return violations
    
    def _check_rule_4(self, x_values: List[float], n: int, C_lower: float, C_upper: float) -> List[str]:
        """准则4: 连续15点落中心线两侧的C区内"""
        violations = []
        if n >= 15:
            for i in range(n - 14):
                all_in_c = all(C_lower <= x_values[i+j] <= C_upper for j in range(15))
                if all_in_c:
                    violations.append(f"准则4: 第{i+1}-{i+15}点全部落在C区内")
        return violations
    
    def _check_rule_5(
        self, x_values: List[float], n: int, cl: float, C_lower: float, C_upper: float
    ) -> List[str]:
        """准则5: 连续8点落在中心两侧且无一在C区内"""
        violations = []
        if n >= 8:
            for i in range(n - 7):
                all_outside_c = True
                has_points_above = False
                has_points_below = False
                
                for j in range(8):
                    x = x_values[i+j]
                    if C_lower <= x <= C_upper:
                        all_outside_c = False
                        break
                    if x > cl:
                        has_points_above = True
                    else:
                        has_points_below = True
                
                if all_outside_c and has_points_above and has_points_below:
                    violations.append(f"准则5: 第{i+1}-{i+8}点落在中心两侧且无一在C区内")
        return violations
    
    def _check_rule_6(self, x_values: List[float], n: int, cl: float) -> List[str]:
        """准则6: 连续9点落在中心线同一侧"""
        violations = []
        if n >= 9:
            for i in range(n - 8):
                all_above = all(x_values[i+j] > cl for j in range(9))
                all_below = all(x_values[i+j] < cl for j in range(9))
                
                if all_above:
                    violations.append(f"准则6: 第{i+1}-{i+9}点落在中心线上方")
                if all_below:
                    violations.append(f"准则6: 第{i+1}-{i+9}点落在中心线下方")
        return violations
    
    def _check_rule_7(
        self, x_values: List[float], n: int, B_upper: float, B_lower: float
    ) -> List[str]:
        """准则7: 连续3点中有2点落在中心线同一侧的B区以外"""
        violations = []
        if n >= 3:
            for i in range(n - 2):
                points_above_b = sum(1 for j in range(3) if x_values[i+j] > B_upper)
                points_below_b = sum(1 for j in range(3) if x_values[i+j] < B_lower)
                
                if points_above_b >= 2:
                    violations.append(f"准则7: 第{i+1}-{i+3}点中有{points_above_b}点落在上侧B区以外")
                if points_below_b >= 2:
                    violations.append(f"准则7: 第{i+1}-{i+3}点中有{points_below_b}点落在下侧B区以外")
        return violations
    
    def _check_rule_8(
        self, x_values: List[float], n: int, C_upper: float, C_lower: float
    ) -> List[str]:
        """准则8: 连续5点中有4点落在中心同一侧的C区以外"""
        violations = []
        if n >= 5:
            for i in range(n - 4):
                points_above_c = sum(1 for j in range(5) if x_values[i+j] > C_upper)
                points_below_c = sum(1 for j in range(5) if x_values[i+j] < C_lower)
                
                if points_above_c >= 4:
                    violations.append(f"准则8: 第{i+1}-{i+5}点中有{points_above_c}点落在上侧C区以外")
                if points_below_c >= 4:
                    violations.append(f"准则8: 第{i+1}-{i+5}点中有{points_below_c}点落在下侧C区以外")
        return violations
    
    def _check_r_chart(self, r_values: List[float], uclr: float, lclr: float) -> List[str]:
        """检查R图"""
        violations = []
        for i, r_val in enumerate(r_values):
            if r_val > uclr:
                violations.append(f"R图: 第{i+1}点超出上控制限")
            if r_val < lclr:
                violations.append(f"R图: 第{i+1}点超出下控制限")
            if r_val == 0:
                violations.append(f"R图: 第{i+1}点R值为0")
        return violations
