"""文件组织服务"""

import os
import shutil
from typing import List, Dict, Optional


class FileOrganizer:
    """文件组织服务"""
    
    def organize_by_month(self, files_by_month: Dict[int, List[str]]):
        """
        按月份组织文件：创建月份文件夹并将对应文件移动进去
        
        Args:
            files_by_month: 按月份分组的文件字典 {月份: [文件路径列表]}
        """
        try:
            from ..config.constants import MONTH_NAME_MAP
            
            moved_files = 0
            for month_num, file_list in files_by_month.items():
                if len(file_list) > 1:  # 只有当月存在多个任务时才创建文件夹
                    month_name = MONTH_NAME_MAP.get(month_num, f"{month_num}月")
                    
                    # 创建月份文件夹
                    if not os.path.exists(month_name):
                        os.makedirs(month_name)
                    
                    # 移动文件到对应文件夹
                    for file_path in file_list:
                        if os.path.exists(file_path):
                            filename = os.path.basename(file_path)
                            dst_file = os.path.join(month_name, filename)
                            
                            # 确保目标文件不存在
                            if os.path.exists(dst_file):
                                base_name, ext = os.path.splitext(filename)
                                counter = 1
                                while os.path.exists(os.path.join(month_name, f"{base_name}_{counter}{ext}")):
                                    counter += 1
                                dst_file = os.path.join(month_name, f"{base_name}_{counter}{ext}")
                            
                            shutil.move(file_path, dst_file)
                            moved_files += 1
            
            if moved_files > 0:
                print(f"已移动 {moved_files} 个文件到月份文件夹")
        
        except Exception as e:
            print(f"按月份组织文件时出错: {e}")
