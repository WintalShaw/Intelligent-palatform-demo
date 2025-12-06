# tools/tool_water_algo.py
import streamlit as st
import time


def run(context):
    # 保持这里的延时逻辑不变
    time.sleep(1)
    return "方案生成完毕"


def view(context):
    st.success("💧 智能配注方案已生成")

    if 'df' in context:
        df = context['df']

        # --- 🛠️ 修复开始：自动适配列名 ---

        # 1. 确定我们要用来计算和画热力图的列
        # 优先找 '调整量'，如果没有，就用 '建议配注' (CSV里肯定有这个)
        if '调整量' in df.columns:
            target_col = '调整量'
            metric_label = "总增注量"
        elif '建议配注' in df.columns:
            target_col = '建议配注'
            metric_label = "总建议配注量"
        else:
            target_col = None  # 万一是个空表
            metric_label = "数值统计"

        col1, col2 = st.columns(2)
        with col1:
            st.metric("涉及调整井数", f"{len(df)} 口")

        with col2:
            # 2. 安全计算总和
            if target_col:
                total = df[target_col].sum()
                # format(total, '.1f') 保留一位小数
                st.metric(metric_label, f"{total:.1f} m³")
            else:
                st.metric("数据状态", "无有效数值列")

        # 3. 安全应用样式 (防止报错)
        if target_col:
            try:
                # 针对目标列显示颜色深浅
                st.dataframe(df.style.background_gradient(subset=[target_col], cmap='coolwarm'),
                             use_container_width=True)
            except Exception:
                # 如果样式应用失败（比如列不是数字），直接显示表格
                st.dataframe(df, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)

        # 更新一下摘要
        context[
            'water_summary'] = f"针对 {len(df)} 口井生成了{metric_label}为 {df[target_col].sum() if target_col else 0} m³ 的优化方案。"
        # --- 🛠️ 修复结束 ---