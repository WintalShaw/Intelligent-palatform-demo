# tools/tool_risk_algo.py
import streamlit as st
import time


def run(context):
    time.sleep(1)  # 假装在扫描异常
    return "风险扫描完成"


def view(context):
    st.warning("⚠️ 发现潜在风险点！")

    if 'df' in context:
        df = context['df']
        # 假设 CSV 有 '井号', '风险值', '风险类型'

        # 1. 风险统计图
        if '风险类型' in df.columns:
            risk_counts = df['风险类型'].value_counts()
            st.bar_chart(risk_counts)

        # 2. 高风险列表
        st.write("🔴 **高风险预警清单**")
        if '风险值' in df.columns:
            high_risk = df[df['风险值'] > 0.8]
            st.dataframe(high_risk, use_container_width=True)
            context['risk_summary'] = f"发现 {len(high_risk)} 口高风险井，主要集中在套损风险。"
        else:
            st.dataframe(df)
            context['risk_summary'] = "整体风险可控。"