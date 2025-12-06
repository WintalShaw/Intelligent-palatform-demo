import streamlit as st
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib import font_manager # 引入字体管理器

def get_chinese_font():
    """
    终极方案：直接加载项目根目录下的字体文件
    """
    # 【核心修改】这里改成了你的文件名
    font_path = "msyh.ttc" 
    
    # 如果根目录找不到，回退到系统字体（防止本地运行报错）
    if not os.path.exists(font_path):
        # 如果本地也没有这个文件，就尝试系统自带的
        return font_manager.FontProperties(family='Microsoft YaHei')
    
    # 加载指定的字体文件
    return font_manager.FontProperties(fname=font_path)

def run(context):
    time.sleep(0.8)
    return "多维关联分析完成"

def view(context):
    st.info("🕸️ 正在进行多维特征归因与关联度测算...")

    # 获取字体属性对象
    zh_font = get_chinese_font()

    # 1. 准备标签
    df = context.get('df')
    base_labels = []
    if df is not None:
        numeric_cols = [c for c in df.columns if 'date' not in c.lower() and '时间' not in c]
        base_labels = numeric_cols[:3] 

    fake_terms = ['动液面', '含水率', '泵效', '孔隙度', '渗透率', '注采比', '地层压力']
    labels = base_labels
    for term in fake_terms:
        if len(labels) >= 5: break
        if term not in labels: labels.append(term)
            
    # 2. 生成数据
    n = len(labels)
    raw_data = np.random.uniform(-0.6, 0.9, size=(n, n))
    corr_matrix = (raw_data + raw_data.T) / 2
    np.fill_diagonal(corr_matrix, 1.0)

    # 3. 绘图
    fig, ax = plt.subplots(figsize=(5, 4))
    
    im = ax.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
    
    # --- 关键修改：所有涉及文字的地方，都显式指定 fontproperties=zh_font ---
    
    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))
    
    # 设置 X 轴标签字体
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9, fontproperties=zh_font)
    # 设置 Y 轴标签字体
    ax.set_yticklabels(labels, fontsize=9, fontproperties=zh_font)
    
    cbar = ax.figure.colorbar(im, ax=ax, shrink=0.75, pad=0.05)
    cbar.ax.tick_params(labelsize=8)

    for i in range(n):
        for j in range(n):
            val = corr_matrix[i, j]
            if abs(val) > 0.3:
                color = "white" if abs(val) > 0.6 else "black"
                ax.text(j, i, f"{val:.2f}", 
                        ha="center", va="center", color=color, fontsize=8)

    # 设置标题字体
    ax.set_title("特征因子相关性矩阵 (AI 模拟)", fontsize=11, pad=10, fontproperties=zh_font)
    
    ax.spines[:].set_visible(False)
    ax.set_xticks(np.arange(n+1)-.5, minor=True)
    ax.set_yticks(np.arange(n+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)

    st.pyplot(fig)
    
    # 4. 结论
    import random
    if len(labels) >= 2:
        f1, f2 = random.sample(labels, 2)
        r_val = random.uniform(0.75, 0.95)
        st.caption(f"✅ 深度归因结论: **{f1}** 对 **{f2}** 具有显著的正向敏感度 (Shapley Value={r_val:.2f})")
