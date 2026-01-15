"""SPC年度计划一键生成工具 - 主程序入口"""

import os
import sys
import time
from typing import Dict, List
from pathlib import Path

# 获取主脚本所在目录（项目根目录）
def get_project_root():
    """获取项目根目录"""
    # 获取主模块的文件路径
    main_module = sys.modules.get('__main__')
    if main_module and hasattr(main_module, '__file__') and main_module.__file__:
        main_file = main_module.__file__
        main_dir = os.path.dirname(os.path.abspath(main_file))
        
        # 如果主文件是 run_spc_generator.py，它在项目根目录
        if os.path.basename(main_file) == 'run_spc_generator.py':
            return main_dir
        
        # 如果主文件在 spc_generator 目录中，返回父目录
        if os.path.basename(main_dir) == 'spc_generator':
            return os.path.dirname(main_dir)
        
        # 否则返回主文件所在目录
        return main_dir
    
    # 回退：从当前工作目录向上查找，直到找到包含 spc_generator 的目录
    cwd = os.path.abspath(os.getcwd())
    current = cwd
    while current:
        # 检查当前目录是否包含 spc_generator 子目录
        spc_gen_path = os.path.join(current, 'spc_generator')
        if os.path.exists(spc_gen_path) and os.path.isdir(spc_gen_path):
            return current
        parent = os.path.dirname(current)
        if parent == current:  # 到达根目录
            break
        current = parent
    
    # 最后回退到当前工作目录
    return cwd

# 导入各模块
from .parsers.theoretical_value_parser import TheoreticalValueParser
from .parsers.reference_range_parser import ReferenceRangeParser
from .parsers.excel_plan_reader import ExcelPlanReader
from .calculators.control_limits_calculator import ControlLimitsCalculator
from .generators.standard_generator import StandardGenerator
from .generators.reference_range_generator import ReferenceRangeGenerator
from .processors.difficulty_evaluator import DifficultyEvaluator
from .excel.template_handler import TemplateHandler
from .excel.formula_restorer import FormulaRestorer
from .excel.chart_adjuster import ChartAdjuster
from .excel.worksheet_writer import WorksheetWriter
from .services.spc_service import SPCService
from .services.file_organizer import FileOrganizer
from .services.plan_updater import PlanUpdater
from .utils.file_utils import FileUtils
from .utils.logger import setup_logging, get_logger, get_log_file_path
from .config.constants import MONTH_MAP, MONTH_NAME_MAP


def main():
    """主程序入口"""
    start_time = time.time()
    
    try:
        print("=" * 60)
        print("SPC文件批量生成工具 V3.4 (模块化版本)")
        print("=" * 60)
        
        # 设置工作目录到项目根目录
        project_root = get_project_root()
        os.chdir(project_root)
        file_utils = FileUtils()
        
        # #region agent log
        import json
        log_path = os.path.join(project_root, '.cursor', 'debug.log')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A',
                'location': 'main.py:45',
                'message': '工作目录设置',
                'data': {
                    'project_root': project_root,
                    'current_dir': os.getcwd(),
                    'files_in_dir': os.listdir('.')[:10] if os.path.exists('.') else []
                },
                'timestamp': int(time.time() * 1000)
            }, ensure_ascii=False) + '\n')
        # #endregion
        
        print(f"工作目录: {os.getcwd()}")
        
        # 询问用户是否采用参考分布范围
        print("\n是否采用参考分布范围? (Y/N, 默认N): ", end="")
        choice = input().strip().upper()
        
        use_reference_range = (choice == 'Y')
        
        if use_reference_range:
            print("已启用参考分布范围模式")
            print("注意: 在此模式下，数据生成将确保:")
            print("  1. 125个原始数据中至少100个在参考范围内")
            print("  2. 25个Xbar全部在参考范围内")
            print("  3. 其他要求保持不变")
        else:
            print("使用标准模式")
        
        # 查找所需文件
        # #region agent log
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'B',
                'location': 'main.py:58',
                'message': '查找文件前',
                'data': {
                    'search_dir': os.getcwd(),
                    'all_files': [f for f in os.listdir('.') if f.endswith('.xlsx')]
                },
                'timestamp': int(time.time() * 1000)
            }, ensure_ascii=False) + '\n')
        # #endregion
        
        plan_file = file_utils.find_spc_plan_file()
        
        # #region agent log
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'B',
                'location': 'main.py:70',
                'message': '查找文件后',
                'data': {
                    'plan_file': plan_file,
                    'search_dir': os.getcwd()
                },
                'timestamp': int(time.time() * 1000)
            }, ensure_ascii=False) + '\n')
        # #endregion
        
        if not plan_file:
            print("错误: 未找到SPC推进计划文件")
            print(f"当前目录文件列表: {[f for f in os.listdir('.') if f.endswith('.xlsx')]}")
            input("按回车键退出...")
            return
        
        # 从计划文件名中提取计划名称（去掉扩展名）
        plan_name = os.path.splitext(plan_file)[0]
        
        # 初始化日志系统
        logger = setup_logging(plan_name, project_root)
        log_file_path = get_log_file_path()
        logger.info("=" * 60)
        logger.info("SPC文件批量生成工具 V3.4 (模块化版本)")
        logger.info("=" * 60)
        logger.info(f"工作目录: {os.getcwd()}")
        logger.info(f"计划文件: {plan_file}")
        logger.info(f"日志文件: {log_file_path}")
        if use_reference_range:
            logger.info("已启用参考分布范围模式")
        else:
            logger.info("使用标准模式")
        
        print(f"SPC推进计划文件: {plan_file}")
        
        template_file = file_utils.find_spc_template_file()
        if not template_file:
            error_msg = "错误: 未找到SPC模板文件"
            print(error_msg)
            logger.error(error_msg)
            input("按回车键退出...")
            return
        
        print(f"SPC模板文件: {template_file}")
        
        # 从文件名中提取车间名称和年份
        workshop_name, year = file_utils.extract_workshop_name_and_year(plan_file)
        print(f"年份: {year}, 车间: {workshop_name}")
        logger.info(f"年份: {year}, 车间: {workshop_name}")
        
        # 初始化各模块
        parser = TheoreticalValueParser()
        ref_range_parser = ReferenceRangeParser()
        calculator = ControlLimitsCalculator()
        standard_generator = StandardGenerator()
        reference_range_generator = ReferenceRangeGenerator()
        excel_handler = TemplateHandler()
        formula_restorer = FormulaRestorer()
        chart_adjuster = ChartAdjuster()
        worksheet_writer = WorksheetWriter()
        difficulty_evaluator = DifficultyEvaluator()
        
        # 创建服务
        spc_service = SPCService(
            parser=parser,
            ref_range_parser=ref_range_parser,
            calculator=calculator,
            standard_generator=standard_generator,
            reference_range_generator=reference_range_generator,
            excel_handler=excel_handler,
            formula_restorer=formula_restorer,
            chart_adjuster=chart_adjuster,
            worksheet_writer=worksheet_writer,
            difficulty_evaluator=difficulty_evaluator
        )
        
        # 读取计划文件
        logger.info("开始读取计划文件...")
        plan_reader = ExcelPlanReader()
        tasks = plan_reader.read_tasks(plan_file)
        approver_info = plan_reader.read_approver_info(plan_file)
        
        print(f"\n找到 {len(tasks)} 个任务")
        logger.info(f"找到 {len(tasks)} 个任务")
        
        # 按月份分组任务
        month_tasks: Dict[int, List] = {}
        for task in tasks:
            for month_name in task.month_status:
                month_num = MONTH_MAP.get(month_name)
                if month_num:
                    if month_num not in month_tasks:
                        month_tasks[month_num] = []
                    month_tasks[month_num].append(task)
        
        print(f"按月份分组: {sorted(month_tasks.keys())}月")
        logger.info(f"按月份分组: {sorted(month_tasks.keys())}月")
        
        # 存储所有结果
        all_results = []
        generated_files = []
        
        # 处理每个月份的任务
        for month_num in sorted(month_tasks.keys()):
            month_name = MONTH_NAME_MAP.get(month_num, f"{month_num}月")
            month_tasks_list = month_tasks[month_num]
            
            print(f"\n处理 {month_name}:")
            print(f"  有 {len(month_tasks_list)} 个任务")
            logger.info(f"开始处理 {month_name}，共 {len(month_tasks_list)} 个任务")
            
            # 处理该月份的每个任务
            for task_idx, task in enumerate(month_tasks_list):
                print(f"\n  任务 {task_idx + 1}/{len(month_tasks_list)}:")
                task_info = f"{task.product_model} - {task.process} - {task.inspection_item}"
                logger.info(f"处理任务 {task_idx + 1}/{len(month_tasks_list)}: {task_info}")
                
                # 为每个任务生成SPC文件
                try:
                    result = spc_service.generate_spc_file(
                        task=task,
                        month_num=month_num,
                        year=year,
                        workshop_name=workshop_name,
                        template_path=template_file,
                        approver_info=approver_info,
                        use_reference_range=use_reference_range
                    )
                    
                    if result:
                        file_path, adjusted_target_cpk, difficulty, actual_cpk = result
                        logger.info(f"任务 {task_idx + 1} 生成成功: {os.path.basename(file_path)}")
                    else:
                        logger.warning(f"任务 {task_idx + 1} 生成失败: 返回None")
                        continue
                except Exception as e:
                    error_msg = f"任务 {task_idx + 1} 生成失败: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    print(f"  错误: {error_msg}")
                    continue
                
                if result:
                    
                    # 记录生成的文件
                    file_info = {
                        'month': month_num,
                        'month_name': month_name,
                        'filename': os.path.basename(file_path),
                        'full_path': os.path.abspath(file_path),
                        'product_model': task.product_model,
                        'process': task.process,
                        'inspection_item': task.inspection_item,
                        'target_cpk': adjusted_target_cpk,
                        'actual_cpk': actual_cpk,
                        'difficulty': difficulty,
                        'use_reference_range': use_reference_range
                    }
                    generated_files.append(file_info)
                    
                    # 记录结果用于更新原计划文件
                    all_results.append({
                        'row_index': task.row_index,
                        'month_num': month_num,
                        'actual_cpk': actual_cpk,
                        'adjusted_target_cpk': adjusted_target_cpk,
                        'difficulty': difficulty,
                        'product_model': task.product_model,
                        'process': task.process
                    })
        
        # 按月份组织文件
        if generated_files:
            logger.info("开始按月份组织文件...")
            file_organizer = FileOrganizer()
            files_by_month = {}
            for file_info in generated_files:
                month_num = file_info['month']
                if month_num not in files_by_month:
                    files_by_month[month_num] = []
                files_by_month[month_num].append(file_info['full_path'])
            
            file_organizer.organize_by_month(files_by_month)
            logger.info(f"文件组织完成，共 {len(generated_files)} 个文件")
        
        # 输出统计信息
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print("\n" + "=" * 60)
        print("处理完成!")
        print(f"共生成 {len(generated_files)} 个SPC文件")
        logger.info("处理完成!")
        logger.info(f"共生成 {len(generated_files)} 个SPC文件")
        
        # 按月份分组统计
        month_stats = {}
        for file_info in generated_files:
            month_name = file_info['month_name']
            if month_name not in month_stats:
                month_stats[month_name] = 0
            month_stats[month_name] += 1
        
        for month_name in sorted(month_stats.keys(), key=lambda x: MONTH_MAP.get(x, 0)):
            count = month_stats[month_name]
            folder_status = "（已创建文件夹）" if count > 1 else ""
            print(f"  {month_name}: {count}个文件{folder_status}")
        
        # 统计参考分布范围模式使用情况
        ref_range_count = sum(
            1 for f in generated_files 
            if f.get('use_reference_range', False)
        )
        if ref_range_count > 0:
            print(f"其中 {ref_range_count} 个文件使用了参考分布范围模式")
        
        # 统计难度分布
        difficulty_stats = {}
        for file_info in generated_files:
            difficulty = file_info.get('difficulty', '未知')
            if difficulty not in difficulty_stats:
                difficulty_stats[difficulty] = 0
            difficulty_stats[difficulty] += 1
        
        if difficulty_stats:
            print("难度分布:")
            for difficulty, count in difficulty_stats.items():
                print(f"  {difficulty}: {count}个文件")
        
        print(f"总耗时: {elapsed_time:.2f}秒")
        logger.info(f"总耗时: {elapsed_time:.2f}秒")
        
        # 询问是否更新年度计划文件
        if all_results:
            print("\n" + "-" * 60)
            update_choice = input("是否更新SPC推进计划文件? (Y/N, 默认Y): ").strip().upper()
            logger.info(f"用户选择更新计划文件: {update_choice}")
            
            if update_choice != 'N':
                logger.info("开始更新SPC推进计划文件...")
                plan_updater = PlanUpdater()
                plan_updater.update_spc_plan_file(plan_file, all_results)
                logger.info("SPC推进计划文件更新完成")
            else:
                print("用户选择不更新SPC推进计划文件")
                logger.info("用户选择不更新SPC推进计划文件")
        
        print("=" * 60)
        logger.info(f"日志文件已保存: {log_file_path}")
        
    except Exception as e:
        error_msg = f"程序运行出错: {e}"
        print(error_msg)
        logger.error(error_msg, exc_info=True)
        import traceback
        traceback.print_exc()
    
    input("\n按回车键退出...")


if __name__ == "__main__":
    main()
