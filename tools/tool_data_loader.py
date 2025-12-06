# tools/tool_data_loader.py
import pandas as pd
import os
import streamlit as st
import time


def run(context):
    file_name = context.get('target_file', '')
    # 假设 CSV 都在 data 目录下
    file_path = os.path.join("data", file_name)

    time.sleep(0.5)  # 模拟加载耗时

    if os.path.exists(file_path):
        # 读取 CSV
        df = pd.read_csv(file_path)
        # 将数据存入上下文，供后续工具使用
        context['df'] = df
        return f"成功加载文件: {file_name}"
    # else:
    #     # 【容错】如果文件不存在，生成一个假的，防止演示翻车
    #     context['file_missing'] = True
    #     return "文件未找到，将使用模拟数据生成器"


def view(context):
    if context.get('file_missing'):
        st.warning(f"⚠️ 未找到文件: {context.get('target_file')}，已自动切换至模拟数据模式。")
    else:
        st.success(f"📂 数据已加载")

    # if 'df' in context:
    #     st.dataframe(context['df'].head(5), use_container_width=True)
    #     st.caption(f"共加载 {len(context['df'])} 条记录")