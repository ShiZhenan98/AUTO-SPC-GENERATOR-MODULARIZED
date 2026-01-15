"""日期工具"""

from datetime import datetime, timedelta
from typing import List


class DateUtils:
    """日期处理工具类"""
    
    @staticmethod
    def generate_month_dates(year: int, month: int, num_dates: int = 25) -> List[str]:
        """
        生成指定月份的连续日期
        
        Args:
            year: 年份
            month: 月份 (1-12)
            num_dates: 需要生成的日期数量
            
        Returns:
            日期字符串列表，格式如"12/9"
        """
        dates = []
        current_date = datetime(year, month, 1)
        
        for i in range(num_dates):
            # 如果日期超出当月，则重置到下个月1号
            if current_date.month != month:
                current_date = datetime(year, month, 1)
            
            # 格式化为"月份/日期"，如"12/9"
            date_str = f"{current_date.month}/{current_date.day}"
            dates.append(date_str)
            
            # 增加一天
            current_date += timedelta(days=1)
        
        return dates
    
    @staticmethod
    def get_month_end_date(year: int, month: int) -> datetime:
        """
        获取指定月份的最后一天
        
        Args:
            year: 年份
            month: 月份 (1-12)
            
        Returns:
            月份最后一天的datetime对象
        """
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        
        # 减去一天得到当月最后一天
        month_end = next_month - timedelta(days=1)
        return month_end
    
    @staticmethod
    def format_month_end_date(year: int, month: int, format_str: str = None) -> str:
        """
        格式化月份最后一天
        
        Args:
            year: 年份
            month: 月份
            format_str: 格式字符串，如"%Y.%m.%d"
            
        Returns:
            格式化后的日期字符串
        """
        month_end = DateUtils.get_month_end_date(year, month)
        if format_str is None:
            format_str = f"{year}.%m.%d"
        return month_end.strftime(format_str)
