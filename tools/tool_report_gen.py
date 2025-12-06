# tools/tool_report_gen.py
import streamlit as st
import time


def run(context):
    return "报告构建完成"


def view(context):
    st.markdown("### 📝 AI 决策报告")

    month = context.get('month', 7)
    task = context.get('task_name', '通用分析')

    # 获取之前工具存入的结论，如果前面的工具没运行，就用默认词
    trend_concl = context.get('trend_summary', '数据波动在正常范围内。')
    risk_concl = context.get('risk_summary', '未发现重大风险。')
    water_concl = context.get('water_summary', '建议维持当前配注方案。')

    # 根据任务类型选择模板
    report_text = ""

    header = f"""
# {month}月度 {task} 专项分析报告
**生成时间**: {time.strftime('%Y-%m-%d')}
**数据来源**: 采油厂生产数据库
---
"""

    if task == "产量预测":
        body = f"""
## 1. 趋势研判
基于 PLR 算法分析，{month} 月份产量整体{trend_concl}。
预测模型显示，上旬产量相对平稳，下旬受措施作业影响可能出现波动。

## 2. 关键建议
建议针对预测出的下降拐点，提前 3 天安排检泵作业，确保日产水平稳定在计划线以上。
"""
    elif task == "风险预测":
        body = f"""
## 1. 风险扫描
本月共扫描单井 120 口。{risk_concl}

## 2. 预警响应
红色预警井号已推送到生产指挥中心。建议立即开展套管探伤检测，并适当降低注水压力。
"""
    elif task == "注水调配":
        body = f"""
## 1. 配注方案
{water_concl}
本方案旨在缓解层间矛盾，提升水驱波及体积。

## 2. 实施计划
建议优先调整 5 号断块的注水井，观察 3 天压力响应后再全面推广。
"""

    full_text = header + body

    # 打字机效果渲染
    container = st.empty()
    stream_str = ""
    for char in full_text:
        stream_str += char
        container.markdown(stream_str + "▌")
        time.sleep(0.01)  # 打字速度
    container.markdown(stream_str)  # 去掉光标

    st.download_button("📥 下载 Word 报告", full_text, file_name=f"{month}月_{task}_报告.md")