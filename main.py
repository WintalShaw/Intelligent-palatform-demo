
import streamlit as st
import importlib
import time
import random
import json
import os
import datetime
import graphviz
from agent_brain import plan_workflow

# ==========================================
# 0. 全局配置与文件路径
# ==========================================
st.set_page_config(page_title="AI油气生产指挥系统 (Ent)", layout="wide", page_icon="🛢️")

USER_DB_FILE = "users.json"
REPORT_DB_FILE = "reports.json"

TOOL_META = {
    "tool_data_loader": {"name": "多源数据集成加载", "icon": "📂"},
    "tool_data_cleaner": {"name": "异常值清洗引擎", "icon": "🧹"},
    "tool_feature_eng": {"name": "时序特征工程构建", "icon": "🔧"},
    "tool_correlation": {"name": "多维因子关联分析", "icon": "🕸️"},
    "tool_model_inference": {"name": "深度学习模型推理", "icon": "🧠"},
    "tool_trend_algo": {"name": "产量趋势预测算法", "icon": "📈"},
    "tool_risk_algo": {"name": "生产风险扫描引擎", "icon": "⚠️"},
    "tool_water_algo": {"name": "智能配注优化模型", "icon": "💧"},
    "tool_report_gen": {"name": "AI 决策报告生成", "icon": "📝"},
    "tool_approval_flow": {"name": "自动审批流程推送", "icon": "📤"},
}

MODELS_LIST = [
    {"id": "model_trend", "name": "产量趋势预测模型 (LSTM-V2)", "last_update": "2024-05-20"},
    {"id": "model_risk", "name": "风险预警分类器 (XGBoost)", "last_update": "2024-06-01"},
    {"id": "model_water", "name": "配注优化强化学习模型 (DQN)", "last_update": "2024-04-15"},
]

# --- CSS 样式 ---
st.markdown("""
<style>
    .stSpinner > div {border-top-color: #0f52ba !important;}
    .element-container {margin-bottom: 10px;}
    .notification-box {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        border-left: 5px solid #ff4b4b;
        background-color: #ffeaea;
    }
    div[data-testid="stExpander"] details {
        border: 1px solid #ff4b4b;
        border-radius: 5px;
        background-color: #fff5f5;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 1. 数据存取与初始化逻辑
# ==========================================
def init_db():
    default_users = {
        "mr.gong": {"password": "123456", "role": "admin", "model_path": "/root/admin/"},
        "user": {"password": "123", "role": "user", "model_path": "/usr/local/user/"}
    }

    if not os.path.exists(USER_DB_FILE):
        # 加上 encoding='utf-8'
        with open(USER_DB_FILE, "w", encoding='utf-8') as f:
            json.dump(default_users, f, ensure_ascii=False, indent=4)
    else:
        # 读取也要加
        with open(USER_DB_FILE, "r", encoding='utf-8') as f:
            users = json.load(f)
        if "mr.gong" not in users:
            users["mr.gong"] = default_users["mr.gong"]
            with open(USER_DB_FILE, "w", encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=4)

    if not os.path.exists(REPORT_DB_FILE):
        # 加上 encoding='utf-8'
        with open(REPORT_DB_FILE, "w", encoding='utf-8') as f:
            json.dump([], f)


def load_data(file):
    # 加上 encoding='utf-8'
    with open(file, "r", encoding='utf-8') as f:
        return json.load(f)


def save_data(file, data):
    with open(file, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def submit_report_to_manager(username, task_name, context):
    """普通用户提交报告"""
    reports = load_data(REPORT_DB_FILE)
    new_report = {
        "id": f"RPT-{int(time.time())}",
        "submitter": username,
        "task_name": task_name,
        "submit_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
         "status": "pending",
        "feedback": "",
        "file_path": context.get('target_file', '未知文件.csv'),
        # 简单模拟报告内容
        "summary": context.get('trend_summary') or context.get('risk_summary') or context.get(
            'water_summary') or "自动生成的分析报告"
    }
    reports.insert(0, new_report)  # 最新在最前
    save_data(REPORT_DB_FILE, reports)


def init_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None  # user 或 admin
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "login"


# ==========================================
# 2. 页面：登录页
# ==========================================
def render_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://img.icons8.com/fluency/96/oil-pump.png", width=80)
        st.title("AI 油气生产指挥系统")
        st.caption("Enterprise Edition V3.2")

        tab1, tab2 = st.tabs(["🔐 账号登录", "📝 员工注册"])
        users = load_data(USER_DB_FILE)

        # --- 登录 ---
        with tab1:
            username = st.text_input("用户名", key="login_user")
            password = st.text_input("密码", type="password", key="login_pass")
            if st.button("登录", use_container_width=True):
                if username in users and users[username]['password'] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = users[username].get('role', 'user')

                    # 路由判断
                    if st.session_state.role == 'admin':
                        st.session_state.current_page = "manager_dashboard"
                        st.success(f"欢迎宫老师！正在进入审批工作台...")
                    else:
                        st.session_state.current_page = "analysis"
                        st.success(f"登录成功！正在加载 {username} 的工作环境...")

                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("用户名或密码错误")

        # --- 注册 (屏蔽 mr.wang) ---
        with tab2:
            new_user = st.text_input("设置用户名", key="reg_user")
            new_pass = st.text_input("设置密码", type="password", key="reg_pass")
            if st.button("注册并初始化", use_container_width=True):
                if new_user.lower() == "mr.wang" or "admin" in new_user.lower():
                    st.error("❌ 无法注册管理层账号，请联系IT部门。")
                elif new_user in users:
                    st.error("用户已存在")
                elif new_user and new_pass:
                    with st.spinner(f"正在为 {new_user} 分配独立空间..."):
                        time.sleep(1)
                        users[new_user] = {
                            "password": new_pass,
                            "role": "user",
                            "model_path": f"/usr/local/ai_models/{new_user}/"
                        }
                        save_data(USER_DB_FILE, users)
                    st.success("注册成功！请登录。")


# ==========================================
# 3. 页面：侧边栏 (包含消息通知)
# ==========================================
# ==========================================
# 3. 页面：侧边栏 (包含消息通知 + 工具库)
# ==========================================
def render_sidebar():
    with st.sidebar:
        if st.session_state.role == 'user':
            reports = load_data(REPORT_DB_FILE)
            # 筛选：当前用户 + 状态是 rejected
            rejected_list = [r for r in reports if
                             r['submitter'] == st.session_state.username and r.get('status') == 'rejected']

            if rejected_list:
                st.error(f"🔔 您有 {len(rejected_list)} 条驳回通知")
                with st.expander("查看驳回详情", expanded=True):
                    for r in rejected_list:
                        st.markdown(f"""
                                <div class="notification-box">
                                    <small>任务: {r['task_name']}</small><br>
                                    <strong>❌ 意见: {r.get('feedback', '无')}</strong>
                                </div>
                                """, unsafe_allow_html=True)

                    # 只有点击这个按钮，才把这些驳回的消息清除（归档或物理删除，这里为了演示直接物理删除）
                    if st.button("我知道了 (清除通知)", key="cls_msg", use_container_width=True):
                        # 逻辑：保留那些【不是(当前用户且被驳回)】的报告
                        new_reports = [
                            x for x in reports
                            if not (x['submitter'] == st.session_state.username and x.get('status') == 'rejected')
                        ]
                        save_data(REPORT_DB_FILE, new_reports)
                        st.rerun()
                st.divider()
        st.title("🛢️ AI 指挥官 Ent")

        # --- 用户信息 ---
        role_icon = "👨‍💼" if st.session_state.role == 'admin' else "👷"
        role_name = "生产经理" if st.session_state.role == 'admin' else "生产工程师"

        with st.container(border=True):
            st.write(f"{role_icon} **用户**: {st.session_state.username}")
            st.caption(f"身份: {role_name}")

        # --- 消息通知区域 (仅普通用户) ---
        if st.session_state.role == 'user':
            reports = load_data(REPORT_DB_FILE)
            rejected = [r for r in reports if r['submitter'] == st.session_state.username and r['status'] == 'rejected']

            if rejected:
                st.divider()
                st.markdown("### 🔔 消息通知")
                for r in rejected:
                    st.markdown(f"""
                    <div class="notification-box">
                        <strong>❌ 审批驳回</strong><br>
                        <small>任务: {r['task_name']}</small><br>
                        <small>意见: {r['feedback']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                if st.button("清除通知"):
                    st.toast("通知已标记为已读")

        st.divider()

        # --- 导航 ---
        if st.session_state.role == 'user':
            st.markdown("### 🧭 导航菜单")
            if st.button("📊 生产分析", use_container_width=True,
                         type="primary" if st.session_state.current_page == "analysis" else "secondary"):
                st.session_state.current_page = "analysis"
                st.rerun()
            if st.button("🔧 参数微调", use_container_width=True,
                         type="primary" if st.session_state.current_page == "training" else "secondary"):
                st.session_state.current_page = "training"
                st.rerun()

            if st.session_state.current_page == "analysis":
                st.write("")  # 增加一点空行
                if st.button("🗑️ 重置/清空工作台", use_container_width=True):
                    # 1. 清空工作流列表
                    st.session_state.workflow = []
                    # 2. 清空上下文数据
                    st.session_state.context = {}
                    # 3. 清除防止重复提交的标记 (如果有的话)
                    keys_to_del = [k for k in st.session_state.keys() if k.startswith("submitted_")]
                    for k in keys_to_del:
                        del st.session_state[k]

                    st.toast("工作台已重置")
                    time.sleep(0.5)
                    st.rerun()

            # --- 【加回】工具库展示 ---
            st.divider()
            st.markdown("### 🧰 已激活工具")
            for tid, meta in TOOL_META.items():
                st.text(f"{meta['icon']} {meta['name']}")

        st.divider()
        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            st.session_state.current_page = "login"
            st.rerun()

# ==========================================
# 4. 页面：王经理审批工作台 (新功能)
# ==========================================
# main.py 中的 render_manager_page 函数替换版

# ==========================================
# 4. 页面：王经理审批工作台 (逻辑升级版)
# ==========================================
def render_manager_page():
    st.title("👨‍💼 生产经理审批工作台")
    st.caption(f"当前用户: 宫老师 (mr.gong) | 部门: 生产运行科 | 权限: Level-5")

    # --- [新增] 统计数据持久化逻辑 ---
    STATS_FILE = "manager_stats.json"

    # 1. 初始化或读取统计数据
    if not os.path.exists(STATS_FILE):
        # 如果文件不存在，给一个初始值（比如本周已经处理了15个），假装系统一直在运行
        stats_data = {"processed_count": 15}
        with open(STATS_FILE, "w", encoding='utf-8') as f:
            json.dump(stats_data, f)
    else:
        with open(STATS_FILE, "r", encoding='utf-8') as f:
            stats_data = json.load(f)

    current_processed = stats_data.get("processed_count", 15)

    # 2. 读取报告数据
    reports = []
    if os.path.exists("reports.json"):
        with open("reports.json", "r", encoding='utf-8') as f:
            reports = json.load(f)

    # 3. 顶部仪表盘
    pending_count = len(reports)
    col1, col2, col3 = st.columns(3)
    col1.metric("待处理审批", pending_count, delta="实时更新" if pending_count > 0 else "无积压", delta_color="inverse")

    # 【修改点】这里不再随机，而是读取真实记录的数字
    col2.metric("本周已处理", current_processed, delta="+1" if 'just_processed' in st.session_state else None)

    # 清除刚才的 +1 动画状态
    if 'just_processed' in st.session_state:
        del st.session_state['just_processed']

    col3.metric("系统健康度", "98.5%")

    st.divider()

    # 4. 如果没有报告
    if not reports:
        st.container(border=True).info("🍵 当前工作台空空如也，您可以喝杯茶休息一下。")
        if st.button("🔄 刷新数据"):
            st.rerun()
        return

    # 5. 待办列表 (遍历显示)
    st.subheader(f"📋 待办事项 ({pending_count})")

    # 使用副本遍历，防止删除时索引错位
    # 注意：这里直接用enumerate可能会有删除索引问题，演示版简单处理即可
    for i, report in enumerate(reports):
        if report.get('status') != 'pending':
            continue
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])

            # 左侧：报告详情
            with c1:
                st.markdown(f"### 📑 {report['task_name']}")
                st.caption(
                    f"提交人: **{report['submitter']}** | 提交时间: {report['submit_time']} | ID: {report['id']}")

                # 摘要框
                st.text_area("AI 分析结论摘要", report['summary'], height=60, disabled=True, key=f"txt_{i}")

                # 模拟附件下载
                # 模拟附件下载
                # 【修复】优先读 file_path，读不到就读 file_name，再读不到就给默认值
                safe_name = report.get('file_path', report.get('file_name', 'report.csv'))

                st.download_button(
                    label="📥 下载完整数据包 (.csv)",
                    data="Simulated Content",
                    file_name=safe_name,
                    key=f"dl_{i}"
                )

            # 右侧：审批操作
            with c2:
                st.write("")  # 占位
                st.write("")

                # --- 定义一个更新统计数据的内部函数 ---
                def update_stats():
                    new_count = current_processed + 1
                    with open(STATS_FILE, "w", encoding='utf-8') as f:
                        json.dump({"processed_count": new_count}, f)
                    st.session_state['just_processed'] = True  # 触发UI上的绿色小箭头

                # --- 同意按钮 ---
                if st.button("✅ 批准执行", key=f"app_{i}", type="primary", use_container_width=True):
                    # 1. 更新统计 (数字+1)
                    update_stats()

                    # 2. 删除报告
                    reports.pop(i)
                    with open("reports.json", "w", encoding='utf-8') as f:
                        json.dump(reports, f, ensure_ascii=False, indent=4)

                    st.toast("审批已通过！报告已归档。")
                    time.sleep(0.5)
                    st.rerun()

                # --- 驳回按钮 ---
                if st.button("❌ 驳回重做", key=f"rej_{i}", use_container_width=True):
                    # 1. 更新统计 (数字+1)
                    update_stats()

                    # 2. 【关键修改】不删除，而是改状态，并写入反馈意见
                    reports[i]['status'] = 'rejected'
                    # 这里为了演示简单写死，你也可以加个 st.text_input 让经理输入
                    reports[i]['feedback'] = "数据特征工程存在异常，请重新检查相关性分析结果。"

                    # 3. 保存回文件
                    save_data(REPORT_DB_FILE, reports)

                    st.toast("已驳回！通知已发送给提交人。")
                    time.sleep(0.5)
                    st.rerun()


def render_training_page():
    st.title("🔧 工具参数更新与微调中心")
    st.caption(f"当前工作空间: {st.session_state.username}@cluster-08")

    col_list, col_detail = st.columns([1, 2])

    # 左侧：选择模型
    with col_list:
        st.subheader("🛠️ 已部署模型库")
        selected_model = st.radio(
            "选择要更新的工具/模型:",
            [m["name"] for m in MODELS_LIST],
            label_visibility="collapsed"
        )

        # 找到对应的模型ID
        model_info = next(item for item in MODELS_LIST if item["name"] == selected_model)

        st.info(f"上次更新时间: {model_info['last_update']}")
        st.warning("提示: 更新参数将触发热加载，不影响当前生产任务。")

    # 右侧：上传与更新面板
    with col_detail:
        with st.container(border=True):
            st.subheader(f"🚀 更新向导: {selected_model}")

            # 步骤 1: 上传
            st.markdown("**Step 1: 上传增量训练数据 (CSV)**")
            uploaded_file = st.file_uploader("拖拽文件到此处", type=["csv"])

            # 步骤 2: 验证与更新
            if uploaded_file is not None:
                st.success(f"✅ 文件已校验: {uploaded_file.name} (12.8 MB)")

                st.markdown("**Step 2: 执行参数更新**")

                # 更新按钮
                if st.button("⚡ 开始微调 (Fine-tuning)", type="primary"):
                    progress_text = "任务初始化中..."
                    my_bar = st.progress(0, text=progress_text)

                    # --- 模拟训练过程 ---
                    steps = [
                        ("正在读取 CSV 数据...", 0.5),
                        ("数据清洗与归一化...", 1.0),
                        (f"加载用户 {st.session_state.username} 的私有权重...", 1.0),
                        ("启动反向传播 (Epoch 1/5)...", 1.5),
                        ("启动反向传播 (Epoch 5/5)...", 1.5),
                        ("验证集评估 (Accuracy: 98.2%)...", 1.0),
                        ("参数序列化与热部署...", 1.0)
                    ]

                    total_steps = len(steps)
                    for i, (msg, sleep_time) in enumerate(steps):
                        # 进度条逻辑
                        percent = int(((i) / total_steps) * 100)
                        my_bar.progress(percent, text=f"🔄 {msg}")
                        time.sleep(sleep_time)

                    my_bar.progress(100, text="✅ 更新完成")
                    st.balloons()
                    st.success(f"🎉 模型 `{selected_model}` 参数已更新至版本 V{random.randint(3, 9)}.0！")
# ==========================================
# 5. 页面：普通用户分析页 (集成提交逻辑)
# ==========================================
# ==========================================
# 5. 页面：普通用户分析页 (含可视化 + 自动提交)
# ==========================================
def render_analysis_page():
    st.title("交互式生产分析平台 V2.0")

    query = st.text_input("请输入指令 (如: '7月产量预测')", "7月产量预测")
    start_btn = st.button("🚀 启动全流程分析", type="primary")

    if 'workflow' not in st.session_state:
        st.session_state.workflow = []
        st.session_state.context = {}

    if start_btn and query:
        # --- 🕒 修改点 1：把编排过程拖长到 5-10 秒 ---
        with st.status("🧠 AI 正在深度解析指令...", expanded=True) as status:
            # 第 1 步：语义理解 (约 2 秒)
            st.write("🔍 正在进行自然语言语义分解...")
            time.sleep(2.0)

            # 第 2 步：知识检索 (约 3 秒)
            st.write("📚 检索油气生产历史知识库...")
            time.sleep(3.0)

            # 第 3 步：生成方案 (约 3 秒)
            st.write("🤖 正在生成多Agent协同工作流...")
            time.sleep(random.uniform(2.0, 4.0))  # 随机再加点时间

            # 真正的后端调用
            wf, ctx = plan_workflow(query)
            st.session_state.workflow = wf
            st.session_state.context = ctx

            status.update(label="✅ 任务编排完成", state="complete", expanded=False)

        st.rerun()

    # --- 执行与可视化逻辑 ---
    if st.session_state.workflow:
        workflow = st.session_state.workflow
        context = st.session_state.context

        # --- 【加回】Graphviz 可视化流程图 ---
        st.divider()
        st.subheader("🗺️ AI 任务编排可视化")

        graph = graphviz.Digraph()
        graph.attr(rankdir='LR')
        graph.attr('node', shape='box', style='filled', fontname='SimHei')  # 使用黑体支持中文

        for tool_id in workflow:
            meta = TOOL_META.get(tool_id, {"name": tool_id, "icon": "🔧"})

            # 根据工具类型上色
            if "loader" in tool_id or "cleaner" in tool_id:
                fillcolor = "#E1F5FE"
            elif "algo" in tool_id or "model" in tool_id:
                fillcolor = "#FFF9C4"
            elif "report" in tool_id:
                fillcolor = "#C8E6C9"
            else:
                fillcolor = "#F5F5F5"

            graph.node(tool_id, f"{meta['icon']}\n{meta['name']}", fillcolor=fillcolor, fontsize='10')

        # 画线
        for i in range(len(workflow) - 1):
            graph.edge(workflow[i], workflow[i + 1], color='gray')

        st.graphviz_chart(graph, use_container_width=True)
        st.divider()
        # ------------------------------------

        progress_text = "任务执行进度"
        my_bar = st.progress(0, text=progress_text)

        # 记录是否需要提交报告
        need_submit = False

        # 遍历执行工具
        for i, tool_id in enumerate(workflow):
            meta = TOOL_META.get(tool_id, {"name": tool_id, "icon": "🔧"})
            progress_percent = int((i / len(workflow)) * 100)
            my_bar.progress(progress_percent, text=f"执行中: {meta['name']}")

            with st.expander(f"Step {i + 1}: {meta['name']}", expanded=True):
                try:
                    module = importlib.import_module(f"tools.{tool_id}")
                    if not context.get(f"{tool_id}_done"):
                        # 模拟延迟
                        wait_time = 4.0
                        loading_text = f"{meta['name']} 运行中..."

                        # 如果是报告生成工具，改为 10 秒
                        if "report_gen" in tool_id:
                            wait_time = 10.0
                            loading_text = "🧠 AI 正在综合多维数据，撰写决策建议报告 (深度思考中)..."

                        # 执行等待
                        with st.spinner(loading_text):
                            time.sleep(wait_time)  # 执行延时
                            module.run(context)  # 运行工具
                        msg = module.run(context)
                        context[f"{tool_id}_done"] = True
                        st.session_state.context = context

                    if hasattr(module, 'view'):
                        module.view(context)

                    # 检查是否为报告类工具
                    if "report" in tool_id or "approval" in tool_id:
                        need_submit = True

                except Exception as e:
                    st.error(f"Error: {e}")

        my_bar.progress(100, text="✅ 执行完毕")

        # --- 自动提交逻辑 ---
        # task_key = f"submitted_{context.get('task_name')}_{int(time.time() / 600)}"
        # if need_submit and task_key not in st.session_state:
        #     with st.spinner("📤 正在自动推送至王经理审批端..."):
        #         time.sleep(1.5)
        #         submit_report_to_manager(
        #             st.session_state.username,
        #             context.get('task_name', '通用任务'),
        #             context
        #         )
        #         st.session_state[task_key] = True
        #     st.success("✅ 报告已推送！请等待王经理审批。")

# ==========================================
# 7. 主程序入口
# ==========================================
if __name__ == "__main__":
    init_db()  # 初始化文件
    init_session()

    if not st.session_state.logged_in:
        render_login_page()
    else:
        render_sidebar()  # 侧边栏常驻

        # 根据角色和页面路由
        if st.session_state.role == 'admin':
            render_manager_page()
        else:
            if st.session_state.current_page == "analysis":
                render_analysis_page()
            elif st.session_state.current_page == "training":
                render_training_page()
