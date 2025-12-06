# tools/tool_model_inference.py
import streamlit as st
import time
import random

def run(context):
    # 这里不需要sleep，因为我们在view里模拟进度条
    return "推理启动"

def view(context):
    st.write("🧠 正在加载 LSTM-Transformer 混合模型...")
    
    # 模拟一个推理进度条
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 进度条跑动逻辑
    for i in range(101):
        if i % 10 == 0: # 加快一点速度，每10%停顿一下
            time.sleep(0.02)
            progress_bar.progress(i)
            # 动态显示推理百分比
            status_text.text(f"Tensor Core 推理中... {i}%")
            
    # --- 核心修改：生成随机数据 ---
    # 耗时: 0.8 ~ 2.5 秒
    cost_time = random.uniform(0.8, 2.5)
    # 显存: 3.5 ~ 6.2 GB
    vram_usage = random.uniform(3.5, 6.2)
    
    # 显示最终状态 (保留一位或两位小数)
    status_text.text(f"✅ 模型推理完成 | 耗时: {cost_time:.2f}s | 显存占用: {vram_usage:.1f}GB")
