"""图表调整器"""

from ..models.control_limits import ControlLimits


class ChartAdjuster:
    """图表调整器"""
    
    def adjust_chart_axes(self, worksheet, control_limits: ControlLimits):
        """
        调整图表纵坐标轴范围以适应控制限
        
        Args:
            worksheet: 工作表对象
            control_limits: 控制限对象
        """
        try:
            if not control_limits:
                print("    警告: 没有控制限值，跳过图表调整")
                return
            
            # 查找图表对象
            charts = []
            
            if hasattr(worksheet, '_charts'):
                charts = worksheet._charts
            elif hasattr(worksheet, 'charts'):
                charts = worksheet.charts
            elif hasattr(worksheet, 'chart_drawings'):
                charts = worksheet.chart_drawings
            
            if not charts and hasattr(worksheet, 'drawings'):
                for drawing in worksheet.drawings:
                    if hasattr(drawing, '__class__') and 'Chart' in str(drawing.__class__):
                        charts.append(drawing)
            
            # 调整图表坐标轴
            for i, chart in enumerate(charts):
                try:
                    if i == 0:  # Xbar图
                        sigma = control_limits.sigma
                        ucl = control_limits.ucl
                        lcl = control_limits.lcl
                        
                        if sigma != 0 and ucl != 0 and lcl != 0:
                            min_val = lcl - sigma
                            max_val = ucl + sigma
                            
                            if min_val >= max_val:
                                min_val = lcl * 0.9
                                max_val = ucl * 1.1
                            
                            if hasattr(chart, 'y_axis') and chart.y_axis:
                                chart.y_axis.scaling.min = min_val
                                chart.y_axis.scaling.max = max_val
                    
                    elif i == 1:  # R图
                        uclr = control_limits.uclr
                        lclr = control_limits.lclr
                        
                        if uclr != 0 and lclr != 0:
                            control_range = uclr - lclr
                            total_range = control_range / 0.8
                            extra_space = total_range - control_range
                            
                            min_val = lclr - extra_space / 2
                            max_val = uclr + extra_space / 2
                            
                            if min_val < 0:
                                min_val = 0
                            
                            if min_val >= max_val:
                                min_val = 0
                                max_val = uclr * 1.2
                            
                            if hasattr(chart, 'y_axis') and chart.y_axis:
                                chart.y_axis.scaling.min = min_val
                                chart.y_axis.scaling.max = max_val
                
                except Exception:
                    pass
            
        except Exception as e:
            print(f"调整图表坐标轴时出错: {e}")
