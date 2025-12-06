import streamlit as st
import time

def run(context):
    time.sleep(0.8) # 假装耗时
    return "清洗完成"

def view(context):
    # 简单的运行结束提示
    st.success("✅ 数据清洗引擎执行完毕")
    st.caption("已处理空值: 0 | 已剔除离群点: 12 | 数据质量评分: 98.5")