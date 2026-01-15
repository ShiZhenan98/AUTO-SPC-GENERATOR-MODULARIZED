"""常量配置"""

# 控制图常数（子组大小n=5）
D2_CONSTANT = 2.326   # 用于计算σ = R̄/d2
D3_CONSTANT = 0       # R图下控制限系数
D4_CONSTANT = 2.114   # R图上控制限系数

# 默认值
DEFAULT_TARGET_CPK = 1.8
DEFAULT_SUBGROUP_SIZE = 5
DEFAULT_DECIMAL_PLACES = 3

# 月份映射
MONTH_MAP = {
    '1月': 1, '2月': 2, '3月': 3, '4月': 4,
    '5月': 5, '6月': 6, '7月': 7, '8月': 8,
    '9月': 9, '10月': 10, '11月': 11, '12月': 12
}

# 月份名称映射（反向）
MONTH_NAME_MAP = {v: k for k, v in MONTH_MAP.items()}

# 判异准则描述
EIGHT_RULES_DESCRIPTIONS = {
    1: "一点落在A区外（超出3σ控制限）",
    2: "连续6点递增或递减",
    3: "连续14点中相邻点上下交替",
    4: "连续15点落在中心线两侧的C区内",
    5: "连续8点落在中心两侧且无一在C区内",
    6: "连续9点落在中心线同一侧",
    7: "连续3点中有2点落在中心线同一侧的B区以外",
    8: "连续5点中有4点落在中心同一侧的C区以外",
}

# 支持的分辨率
SUPPORTED_RESOLUTIONS = [0.1, 0.01, 0.02, 0.001, 0.0001, 0.00001]

# Excel单元格地址
CELL_ADDRESSES = {
    'workshop': 'D2',
    'product_model': 'D3',
    'product_model_2': 'U3',
    'process': 'I2',
    'theory': 'M3',
    'inspection_item': 'M2',
    'equipment_no': 'I3',
    'usl': 'Q2',
    'lsl': 'Q3',
    'center': 'E4',
    'center_reference': 'C40',
    'sigma': 'H4',
    'ucl': 'J4',
    'lcl': 'L4',
    'ucl1': 'N4',
    'ucl2': 'P4',
    'lcl1': 'R4',
    'lcl2': 'T4',
    'rbar': 'E17',
    'uclr': 'L17',
    'lclr': 'U17',
    'data_start': 'C32',
    'data_end': 'AA36',
    'avg_row': 37,
    'range_row': 38,
    'date_row': 31,
    'preparer': 'C51',
    'auditor': 'J51',
    'approver': 'Q51',
}
