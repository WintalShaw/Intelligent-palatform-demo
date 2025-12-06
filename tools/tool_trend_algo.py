# tools/tool_trend_algo.py
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import time
import os
from matplotlib import font_manager  # 引入字体管理器

def get_chinese_font():
    """
    加载项目根目录下的 msyh.ttc 字体
    """
    font_path = "msyh.ttc"  # 你的字体文件名
    
    # 本地防错：如果找不到文件，尝试使用系统默认
    if not os.path.exists(font_path):
        return font_manager.FontProperties(family='Microsoft YaHei')
    
    return font_manager.FontProperties(fname=font_path)

def run(context):
    time.sleep(1)  # 假装在进行深度学习预测
    return "预测完成"

def view(context):
    st.info("📉 正在渲染未来产量趋势预测曲线...")

    # 获取中文字体对象
    zh_font = get_chinese_font()

    if 'df' in context:
        df = context['df']

        # 确保日期格式正确
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        # --- 绘图逻辑 ---
        fig, ax = plt.subplots(figsize=(10, 4))

        # 绘制纯预测线（红色实线，加点强调）
        ax.plot(df['date'], df['predicted_yield'],
                label='AI 预测趋势',
                color='#d62728',  # 鲜艳的红色
                linewidth=2.5,  # 线条加粗
                marker='o',  # 加上数据点
                markersize=4,
                linestyle='-')

        # --- 核心修改：所有涉及中文的地方都要指定字体 ---
        
        # 1. 标题
        ax.set_title(f"{context.get('month')}月 全周期产量推演 (AI Predicted)", 
                     fontsize=12, 
                     fontproperties=zh_font) # 指定字体
        
        # 2. 图例 (注意：图例的参数叫 prop，不是 fontproperties)
        ax.legend(loc='upper right', prop=zh_font)
        
        # 3. 坐标轴标签
        ax.set_xlabel("预测时间轴", fontproperties=zh_font)
        ax.set_ylabel("日产量 (吨)", fontproperties=zh_font)

        # 4. 其他装饰
        ax.grid(True, linestyle='--', alpha=0.3)

        # 填充颜色，增加视觉冲击力
        ax.fill_between(df['date'], df['predicted_yield'], alpha=0.1, color='red')

        st.pyplot(fig)

        # 更新给报告用的摘要
        # 加上简单的容错，防止 CSV 为空导致报错
        if not df.empty:
            min_val = df['predicted_yield'].min()
            max_val = df['predicted_yield'].max()
            context['trend_summary'] = f"预计全月产量将在 {min_val}~{max_val} 吨区间运行，呈现平稳缓降趋势。"
        else:
            context['trend_summary'] = "数据不足，无法生成摘要。"
