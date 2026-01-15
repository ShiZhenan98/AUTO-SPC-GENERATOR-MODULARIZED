"""SPC生成服务"""

import os
import re
from typing import Optional, Dict, List, Tuple
from ..models.task import Task
from ..models.tolerance import Tolerance
from ..models.control_limits import ControlLimits
from ..models.spc_data import SPCData
from ..parsers.theoretical_value_parser import TheoreticalValueParser
from ..parsers.reference_range_parser import ReferenceRangeParser
from ..calculators.control_limits_calculator import ControlLimitsCalculator
from ..generators.standard_generator import StandardGenerator
from ..generators.reference_range_generator import ReferenceRangeGenerator
from ..processors.difficulty_evaluator import DifficultyEvaluator
from ..excel.template_handler import TemplateHandler
from ..excel.formula_restorer import FormulaRestorer
from ..excel.chart_adjuster import ChartAdjuster
from ..excel.worksheet_writer import WorksheetWriter
from ..utils.file_utils import FileUtils


class SPCService:
    """SPC生成服务 - 协调各模块完成文件生成"""
    
    def __init__(
        self,
        parser: TheoreticalValueParser,
        ref_range_parser: ReferenceRangeParser,
        calculator: ControlLimitsCalculator,
        standard_generator: StandardGenerator,
        reference_range_generator: ReferenceRangeGenerator,
        excel_handler: TemplateHandler,
        formula_restorer: FormulaRestorer,
        chart_adjuster: ChartAdjuster,
        worksheet_writer: WorksheetWriter,
        difficulty_evaluator: DifficultyEvaluator
    ):
        self.parser = parser
        self.ref_range_parser = ref_range_parser
        self.calculator = calculator
        self.standard_generator = standard_generator
        self.reference_range_generator = reference_range_generator
        self.excel_handler = excel_handler
        self.formula_restorer = formula_restorer
        self.chart_adjuster = chart_adjuster
        self.worksheet_writer = worksheet_writer
        self.difficulty_evaluator = difficulty_evaluator
        self.file_utils = FileUtils()
    
    def generate_spc_file(
        self,
        task: Task,
        month_num: int,
        year: int,
        workshop_name: str,
        template_path: str,
        approver_info: Dict[str, str],
        use_reference_range: bool = False
    ) -> Optional[Tuple[str, float, str, float]]:
        """
        为单个任务生成SPC文件
        
        Args:
            task: 任务信息
            month_num: 月份
            year: 年份
            workshop_name: 车间名称
            template_path: 模板文件路径
            approver_info: 审批人信息
            use_reference_range: 是否使用参考分布范围模式
            
        Returns:
            (文件路径, 调整后的目标CPK, 难度) 元组，失败返回None
        """
        try:
            print(f"  处理: {task.product_model} - {task.process} - {task.inspection_item}")
            print(f"  目标cpk: {task.target_cpk}")
            
            if task.resolution:
                print(f"  分辨率: {task.resolution}")
            
            if task.reference_range:
                print(f"  参考分布范围: {task.reference_range}")
            
            # 步骤1: 解析理论值
            tolerance = self.parser.parse(task.theory)
            if not tolerance.is_valid():
                print(f"    警告: 公差无效")
                return None
            
            print(f"    公差类型: {tolerance.tolerance_type.value}")
            
            # 步骤2: 解析参考分布范围
            ref_lower, ref_upper = None, None
            if task.reference_range:
                ref_lower, ref_upper = self.ref_range_parser.parse(task.reference_range)
            
            # 步骤3: 检查并调整目标cpk（如果开启了参考范围模式）
            adjusted_target_cpk, difficulty = self._check_and_adjust_target_cpk(
                task.target_cpk,
                tolerance,
                ref_lower,
                ref_upper,
                task.product_model,
                task.process,
                use_reference_range
            )
            
            # 步骤4: 计算控制限
            ref_center = None
            if use_reference_range and ref_lower is not None and ref_upper is not None:
                ref_center = (ref_lower + ref_upper) / 2
            
            control_limits = self.calculator.calculate(
                tolerance=tolerance,
                target_cpk=adjusted_target_cpk,
                ref_center=ref_center
            )
            
            # 步骤5: 生成SPC数据
            spc_data = None
            
            # 根据难度评估动态设置尝试次数
            if use_reference_range and ref_lower is not None and ref_upper is not None:
                max_attempts = 20000  # 参考范围模式统一使用20000次
                print(f"    难度评估: {difficulty}, 设置尝试次数: {max_attempts}")
                
                spc_data = self.reference_range_generator.generate(
                    tolerance=tolerance,
                    control_limits=control_limits,
                    target_cpk=adjusted_target_cpk,
                    resolution=task.resolution,
                    ref_lower=ref_lower,
                    ref_upper=ref_upper,
                    max_attempts=max_attempts
                )
                
                # 如果参考范围模式失败，自动尝试标准模式作为后备
                if spc_data is None:
                    print(f"    参考范围模式失败，自动尝试标准模式...")
                    spc_data = self.standard_generator.generate(
                        tolerance=tolerance,
                        control_limits=control_limits,
                        target_cpk=adjusted_target_cpk,
                        resolution=task.resolution,
                        max_attempts=max_attempts // 2
                    )
            else:
                spc_data = self.standard_generator.generate(
                    tolerance=tolerance,
                    control_limits=control_limits,
                    target_cpk=adjusted_target_cpk,
                    resolution=task.resolution,
                    max_attempts=4000
                )
            
            if spc_data is None:
                print(f"    警告: 未能生成SPC数据")
                return None
            
            print(f"    实际CPK: {spc_data.actual_cpk:.4f}")
            
            # 步骤6: 生成Excel文件
            wb = self.excel_handler.load_template(template_path)
            ws = wb.active
            
            # 填充基本信息
            self.excel_handler.fill_basic_info(
                ws, workshop_name, task.product_model, task.process,
                task.theory, task.inspection_item, task.equipment_no,
                tolerance, year, month_num
            )
            
            # 设置参考中心（如果需要）
            if use_reference_range and ref_center is not None:
                self.worksheet_writer.set_reference_center(ws, ref_center, use_reference_range)
            
            # 填充测量数据
            self.worksheet_writer.fill_measurement_data(ws, spc_data)
            
            # 填充审批人信息
            from ..config.constants import MONTH_NAME_MAP
            month_name = MONTH_NAME_MAP.get(month_num, f"{month_num}月")
            self.worksheet_writer.fill_approver_info(ws, approver_info, year, month_num)
            
            # 恢复公式
            self.formula_restorer.restore_formulas(
                ws, tolerance, use_reference_range, ref_center
            )
            
            # 调整图表
            self.chart_adjuster.adjust_chart_axes(ws, control_limits)
            
            # 生成文件名
            output_filename = self._generate_filename(
                task, month_name, use_reference_range and ref_lower is not None and ref_upper is not None
            )
            
            # 保存文件
            wb.save(output_filename)
            wb.close()
            
            print(f"    已保存: {output_filename}")
            
            return output_filename, adjusted_target_cpk, difficulty, spc_data.actual_cpk
            
        except Exception as e:
            print(f"    错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _generate_filename(
        self,
        task: Task,
        month_name: str,
        use_reference_range: bool
    ) -> str:
        """生成文件名"""
        safe_product_model = self.file_utils.sanitize_filename(task.product_model, 50)
        safe_process = self.file_utils.sanitize_filename(task.process, 20)
        safe_inspection_item = self.file_utils.sanitize_filename(task.inspection_item, 20)
        
        if not safe_product_model:
            safe_product_model = "产品"
        if not safe_process:
            safe_process = "工序"
        if not safe_inspection_item:
            safe_inspection_item = "检测项目"
        
        mode_suffix = "_参考范围" if use_reference_range else ""
        base_filename = f"{month_name}{safe_product_model}{safe_process}{safe_inspection_item}{mode_suffix}_SPC.xlsx"
        
        return self.file_utils.ensure_unique_filename(base_filename)
    
    def _check_and_adjust_target_cpk(
        self,
        target_cpk: float,
        tolerance: Tolerance,
        ref_lower: Optional[float],
        ref_upper: Optional[float],
        product_model: str,
        process: str,
        use_reference_range: bool
    ) -> Tuple[float, str]:
        """
        检查目标cpk是否在理论范围内，如果不在则询问用户调整
        
        Args:
            target_cpk: 原始目标CPK
            tolerance: 公差信息
            ref_lower: 参考范围下限
            ref_upper: 参考范围上限
            product_model: 产品型号
            process: 工序
            use_reference_range: 是否使用参考范围模式
            
        Returns:
            (调整后的目标CPK, 难度评估)
        """
        if not use_reference_range:
            return target_cpk, "中等"
        
        if ref_lower is None or ref_upper is None:
            return target_cpk, "中等"
        
        print(f"  进行目标cpk可行性检查...")
        
        # 计算理论cpk范围
        cpk_lower, cpk_upper, difficulty = self.difficulty_evaluator.evaluate(
            tolerance, ref_lower, ref_upper, target_cpk
        )
        
        print(f"  理论cpk范围: [{cpk_lower:.4f}, {cpk_upper:.4f}]")
        print(f"  目标cpk: {target_cpk:.4f}")
        print(f"  难度评估: {difficulty}")
        
        # 检查是否在合理范围内
        tolerance_val = 0.01  # 小容差，避免浮点误差
        
        if target_cpk < cpk_lower - tolerance_val:
            print(f"  ⚠️  警告: 目标cpk({target_cpk:.4f})低于理论下限({cpk_lower:.4f})")
            print(f"     参考范围过窄，无法达到如此低的目标cpk")
            
            # 询问用户是否调整
            print(f"  是否调整目标cpk? (Y/N, 默认N): ", end="")
            try:
                adjust_choice = input().strip().upper()
            except:
                adjust_choice = 'N'
            
            if adjust_choice == 'Y':
                # 询问新的目标cpk
                while True:
                    try:
                        new_cpk_str = input(
                            f"  请输入新的目标cpk (建议范围: {cpk_lower:.4f} ~ {cpk_upper:.4f}): "
                        ).strip()
                        new_cpk = float(new_cpk_str)
                        
                        if new_cpk < cpk_lower - tolerance_val:
                            print(f"  输入值仍然低于理论下限，请重新输入")
                            continue
                        elif new_cpk > cpk_upper + tolerance_val:
                            print(f"  输入值高于理论上限，请重新输入")
                            continue
                        else:
                            print(f"  目标cpk已调整为: {new_cpk:.4f}")
                            return new_cpk, difficulty
                    except ValueError:
                        print(f"  输入无效，请输入数字")
                    except KeyboardInterrupt:
                        print(f"\n  用户取消，保持原目标cpk: {target_cpk:.4f}")
                        return target_cpk, difficulty
            else:
                print(f"  保持原目标cpk: {target_cpk:.4f}")
                return target_cpk, difficulty
        
        elif target_cpk > cpk_upper + tolerance_val:
            print(f"  ⚠️  警告: 目标cpk({target_cpk:.4f})高于理论上限({cpk_upper:.4f})")
            print(f"     参考范围过窄或位置不当，无法达到如此高的目标cpk")
            
            # 询问用户是否调整
            print(f"  是否调整目标cpk? (Y/N, 默认N): ", end="")
            try:
                adjust_choice = input().strip().upper()
            except:
                adjust_choice = 'N'
            
            if adjust_choice == 'Y':
                # 询问新的目标cpk
                while True:
                    try:
                        new_cpk_str = input(
                            f"  请输入新的目标cpk (建议范围: {cpk_lower:.4f} ~ {cpk_upper:.4f}): "
                        ).strip()
                        new_cpk = float(new_cpk_str)
                        
                        if new_cpk > cpk_upper + tolerance_val:
                            print(f"  输入值仍然高于理论上限，请重新输入")
                            continue
                        elif new_cpk < cpk_lower - tolerance_val:
                            print(f"  输入值低于理论下限，请重新输入")
                            continue
                        else:
                            print(f"  目标cpk已调整为: {new_cpk:.4f}")
                            return new_cpk, difficulty
                    except ValueError:
                        print(f"  输入无效，请输入数字")
                    except KeyboardInterrupt:
                        print(f"\n  用户取消，保持原目标cpk: {target_cpk:.4f}")
                        return target_cpk, difficulty
            else:
                print(f"  保持原目标cpk: {target_cpk:.4f}")
                return target_cpk, difficulty
        else:
            if difficulty == "高":
                print(f"  ⚠️  难度较高，但目标cpk在理论范围内")
            else:
                print(f"  ✓ 目标cpk在理论范围内，继续执行")
            
            return target_cpk, difficulty
