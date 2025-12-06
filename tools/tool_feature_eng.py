# tools/tool_feature_eng.py
import streamlit as st
import time
import random
import pandas as pd
import numpy as np

def run(context):
    time.sleep(0.8) # 假装耗时
    return "特征构建完成"

def view(context):
    # 1. 获取任务类型和数据列名
    task = context.get('task_name', '')
    df = context.get('df')
    
    # 获取 CSV 中的关键列名（排除日期）
    target_col = "Value"
    if df is not None:
        cols = [c for c in df.columns if 'date' not in c.lower() and '时间' not in c]
        if cols:
            target_col = cols[0] # 取第一列数值列作为特征基底

    # 2. 定义不同场景的“专业术语库”
    # 这些词汇会随机组合，让特征看起来很高级
    
    # 通用时序特征 (General)
    common_feats = [
        f"{target_col}_Lag_1",       # 滞后特征
        f"{target_col}_Lag_7",
        f"{target_col}_MA_15",       # 滑动平均
        f"{target_col}_Std_30",      # 滑动标准差
        f"{target_col}_Diff",        # 一阶差分
        "Time_Embedding_Sin",        # 时间编码
        "Seasonality_Idx"            # 季节性指数
    ]
    
    # 场景 A: 产量趋势 (Production)
    prod_terms = [
        "Arps_Decline_Rate",         # Arps递减率
        "Water_Cut_Derivative",      # 含水率导数
        "Cumulative_Oil_Prod",       # 累产
        "Liquid_Prod_Index",         # 产液指数
        "Natural_Decline_b"          # 自然递减指数
    ]
    
    # 场景 B: 注水调配 (Injection)
    water_terms = [
        "Voidage_Replacement_Ratio", # 注采比
        "Injectivity_Index",         # 吸水指数
        "Hall_Plot_Slope",           # 霍尔曲线斜率
        "Pressure_Gradient",         # 压力梯度
        "Water_Drive_Index"          # 水驱指数
    ]
    
    # 场景 C: 风险预测 (Risk)
    risk_terms = [
        "Anomaly_Score_IsolationForest", # 孤立森林评分
        "Pressure_Surge_Rate",           # 压力激增率
        "Casing_Damage_Prob",            # 套损概率
        "Entropy_Risk_Val",              # 熵值风险
        "Threshold_Crossing_Count"       # 越限次数
    ]

    # 3. 动态组装特征列表
    generated_features = []
    
    # 先加通用的
    generated_features.extend(random.sample(common_feats, k=3))
    
    # 再根据任务类型加专业的
    if "注水" in task:
        generated_features.extend(random.sample(water_terms, k=3))
    elif "风险" in task:
        generated_features.extend(random.sample(risk_terms, k=3))
    else: # 默认为产量预测
        generated_features.extend(random.sample(prod_terms, k=3))

    # 4. 渲染界面
    st.success(f"✅ 时序特征工程构建完成 (共生成 {len(generated_features)} 维特征)")
    
    st.markdown("**已提取关键因子:**")
    
    # 使用 Markdown 的代码块样式显示特征，看起来像代码输出
    # 用 join 把列表变成 `Tag1` `Tag2` 的形式
    tags = " ".join([f"`{feat}`" for feat in generated_features])
    st.markdown(tags)
    
    # 加一点假装的数据统计
    col1, col2, col3 = st.columns(3)
    col1.metric("特征维度", f"{len(generated_features)}", "+2")
    col2.metric("稀疏度", f"{random.randint(5, 15)}%", "-1.2%")
    col3.metric("信息增益 (IG)", f"{random.uniform(0.6, 0.9):.2f}")
