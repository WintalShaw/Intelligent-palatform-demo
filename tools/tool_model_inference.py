import streamlit as st
import time


def run(context):
    # 这里不需要sleep，因为我们在view里模拟进度条
    return "推理启动"


def view(context):
    st.write("🧠 正在加载 LSTM-Transformer 混合模型...")

    # 模拟一个推理进度条
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(101):
        if i % 10 == 0:  # 加快一点速度
            time.sleep(0.02)
            progress_bar.progress(i)
            status_text.text(f"Tensor Core 推理中... {i}%")

    status_text.text("✅ 模型推理完成 | 耗时: 1.2s | 显存占用: 4.2GB")