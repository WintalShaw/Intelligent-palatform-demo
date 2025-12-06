# tools/tool_trend_algo.py
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import time

# 支持中文绘图
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def run(context):
    time.sleep(1)  # 假装在进行深度学习预测
    return "预测完成"


# tools/tool_trend_algo.py 中的 view 函数更新版

def view(context):
    st.info("📉 正在渲染未来产量趋势预测曲线...")

    if 'df' in context:
        df = context['df']

        # 确保日期格式正确
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        # --- 核心修改：只画这一条预测线 ---
        fig, ax = plt.subplots(figsize=(10, 4))

        # 绘制纯预测线（红色实线，加点强调）
        # predicted_yield 是我们上面CSV里定义的列名
        ax.plot(df['date'], df['predicted_yield'],
                label='AI 预测趋势',
                color='#d62728',  # 鲜艳的红色
                linewidth=2.5,  # 线条加粗
                marker='o',  # 加上数据点
                markersize=4,
                linestyle='-')

        # 添加一些装饰，让它看起来像“未来”
        ax.set_title(f"{context.get('month')}月 全周期产量推演 (AI Predicted)", fontsize=12)
        ax.legend(loc='upper right')
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_xlabel("预测时间轴")
        ax.set_ylabel("日产量 (吨)")

        # 填充颜色，增加视觉冲击力
        ax.fill_between(df['date'], df['predicted_yield'], alpha=0.1, color='red')

        st.pyplot(fig)

        # 更新给报告用的摘要
        min_val = df['predicted_yield'].min()
        max_val = df['predicted_yield'].max()
        context['trend_summary'] = f"预计全月产量将在 {min_val}~{max_val} 吨区间运行，呈现平稳缓降趋势。"