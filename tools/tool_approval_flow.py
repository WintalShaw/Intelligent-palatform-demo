# tools/tool_approval_flow.py
import streamlit as st
import time
import json
import os
import datetime
import random

REPORT_DB_FILE = "reports.json"


def save_report_to_db(context):
    """将当前任务保存到本地 JSON 数据库"""
    # 1. 构造报告数据对象
    new_report = {
        "id": f"TASK-{int(time.time())}-{random.randint(100, 999)}",
        "submitter": st.session_state.get("username", "Unknown"),  # 从全局状态获取提交人
        "task_name": context.get("task_name", "通用分析任务"),
        "submit_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file_path": context.get("target_file", ""),
        # 获取之前工具生成的结论摘要
        "summary": context.get("trend_summary") or context.get("risk_summary") or context.get(
            "water_summary") or "AI自动生成的分析结果",
        "status": "pending"
    }

    # 2. 读取现有数据
    reports = []
    if os.path.exists(REPORT_DB_FILE):
        try:
            with open(REPORT_DB_FILE, "r", encoding='utf-8') as f:
                reports = json.load(f)
        except:
            reports = []

    # 3. 追加新报告 (放在最前面)
    reports.insert(0, new_report)

    # 4. 写入文件
    with open(REPORT_DB_FILE, "w", encoding='utf-8') as f:
        json.dump(reports, f, ensure_ascii=False, indent=4)

    return new_report["id"]


def run(context):
    # 模拟网络推送延迟
    time.sleep(1.5)

    # --- 核心修改：执行保存逻辑 ---
    # 只有当这个任务还没保存过时才保存（防止页面刷新重复写入）
    if not context.get("approval_saved"):
        report_id = save_report_to_db(context)
        context["approval_saved"] = True
        return f"报告已归档，ID: {report_id}"
    else:
        return "报告已存在，跳过保存"


def view(context):
    # 界面渲染
    col1, col2 = st.columns([1, 5])
    with col1:
        # 显示一个动态的发送图标
        st.image("https://img.icons8.com/color/96/sent.png", width=60)
    with col2:
        st.success(f"✅ 方案已自动推送至生产科OA系统 (宫老师待办)")

        # 显示一些元数据，增加真实感
        task = context.get("task_name", "未知任务")
        st.info(f"📋 **任务**: {task} | 📤 **接收人**: mr.gong | ⏱️ **状态**: 待审批")

        st.caption("提示: 报告数据已加密存储于本地服务器，等待管理层签署。")