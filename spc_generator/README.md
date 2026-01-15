# SPC年度计划一键生成工具 - 模块化版本

## 项目结构

```
spc_generator/
├── __init__.py
├── README.md
├── config/
│   ├── __init__.py
│   └── constants.py          ✅ 已创建
├── models/
│   ├── __init__.py           ✅ 已创建
│   ├── tolerance.py          ✅ 已创建
│   ├── task.py               ✅ 已创建
│   ├── control_limits.py     ✅ 已创建
│   └── spc_data.py           ✅ 已创建
├── utils/
│   ├── __init__.py           ✅ 已创建
│   ├── file_utils.py         ✅ 已创建
│   ├── date_utils.py         ✅ 已创建
│   └── validation_utils.py   ✅ 已创建
├── parsers/                  ⏳ 待创建
├── calculators/              ⏳ 待创建
├── generators/               ⏳ 待创建
├── processors/               ⏳ 待创建
├── excel/                    ⏳ 待创建
├── services/                 ⏳ 待创建
└── main.py                   ⏳ 待创建
```

## 已完成模块

### 1. 配置文件 (config/)
- ✅ `constants.py` - 常量配置（控制图常数、默认值、月份映射等）

### 2. 数据模型 (models/)
- ✅ `tolerance.py` - 公差数据模型
- ✅ `task.py` - 任务数据模型
- ✅ `control_limits.py` - 控制限数据模型
- ✅ `spc_data.py` - SPC数据模型

### 3. 工具类 (utils/)
- ✅ `file_utils.py` - 文件操作工具
- ✅ `date_utils.py` - 日期处理工具
- ✅ `validation_utils.py` - 验证工具

## 待创建模块

### 4. 解析器层 (parsers/)
需要创建：
- `__init__.py`
- `theoretical_value_parser.py` - 理论值解析器（25种格式）
- `reference_range_parser.py` - 参考范围解析器
- `excel_plan_reader.py` - Excel计划读取器

### 5. 计算器层 (calculators/)
需要创建：
- `__init__.py`
- `control_limits_calculator.py` - 控制限计算器
- `cpk_calculator.py` - CPK计算器
- `eight_rules_checker.py` - 8条判异准则检查器

### 6. 生成器层 (generators/)
需要创建：
- `__init__.py`
- `base_generator.py` - 生成器基类
- `standard_generator.py` - 标准模式生成器
- `reference_range_generator.py` - 参考范围模式生成器
- `subgroup_generator.py` - 子组数据生成器

### 7. 处理器层 (processors/)
需要创建：
- `__init__.py`
- `resolution_processor.py` - 分辨率处理器
- `data_formatter.py` - 数据格式化器
- `difficulty_evaluator.py` - 难度评估器

### 8. Excel操作层 (excel/)
需要创建：
- `__init__.py`
- `template_handler.py` - 模板处理器
- `formula_restorer.py` - 公式恢复器
- `chart_adjuster.py` - 图表调整器
- `approver_extractor.py` - 审批人信息提取器
- `worksheet_writer.py` - 工作表写入器

### 9. 服务层 (services/)
需要创建：
- `__init__.py`
- `spc_service.py` - SPC生成服务
- `file_organizer.py` - 文件组织服务
- `plan_updater.py` - 计划更新服务

### 10. 主程序
- `main.py` - 主程序入口

## 下一步

由于原代码超过2600行，完整重构需要：
1. 继续创建剩余的解析器模块
2. 创建计算器模块
3. 创建生成器模块（最复杂）
4. 创建Excel操作模块
5. 创建服务层
6. 创建主程序

建议按以下顺序完成：
1. 先完成解析器层（parsers/）
2. 完成计算器层（calculators/）
3. 完成生成器层（generators/）
4. 完成处理器层（processors/）
5. 完成Excel操作层（excel/）
6. 完成服务层（services/）
7. 最后创建主程序（main.py）

## 使用说明

重构完成后，使用方法：

```python
from spc_generator.main import main

if __name__ == "__main__":
    main()
```

或直接运行：
```bash
python -m spc_generator.main
```
