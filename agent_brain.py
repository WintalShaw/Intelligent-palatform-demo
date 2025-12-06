# agent_brain.py
import re


def plan_workflow(query):
    context = {}
    workflow = []

    # 1. 提取月份 (逻辑不变)
    cn_num = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '十一': 11,
              '十二': 12}
    match = re.search(r'(\d+|[一二三四五六七八九十]+)月', query)
    if match:
        val = match.group(1)
        month = int(val) if val.isdigit() else cn_num.get(val, 7)
    else:
        month = 7
    context['month'] = month

    # 2. 构建“长”工具链
    # 公共前置步骤：加载 -> 清洗 -> 特征工程 -> 关联分析 -> 模型推理
    common_prefix = [
        "tool_data_loader",
        "tool_data_cleaner",
        "tool_feature_eng",
        "tool_correlation",
        "tool_model_inference"
    ]

    # 公共后置步骤：报告 -> 审批
    common_suffix = [
        "tool_report_gen",
        "tool_approval_flow"
    ]

    if "注水" in query:
        context['task_name'] = "注水调配"
        context['target_file'] = f"{month}月+注水调配.csv"
        # 核心是 tool_water_algo
        workflow = common_prefix + ["tool_water_algo"] + common_suffix

    elif "风险" in query:
        context['task_name'] = "风险预测"
        context['target_file'] = f"{month}月+风险预测.csv"
        # 核心是 tool_risk_algo
        workflow = common_prefix + ["tool_risk_algo"] + common_suffix

    else:  # 产量趋势
        context['task_name'] = "产量预测"
        context['target_file'] = f"{month}月+产量预测.csv"
        # 核心是 tool_trend_algo
        workflow = common_prefix + ["tool_trend_algo"] + common_suffix

    return workflow, context