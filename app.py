import streamlit as st
import time
import pandas as pd
from datetime import datetime

# 初始化会话状态（避免页面刷新后数据丢失）
if "heartbeat_data" not in st.session_state:
    st.session_state.heartbeat_data = []
if "last_receive_time" not in st.session_state:
    st.session_state.last_receive_time = time.time()
if "is_offline" not in st.session_state:
    st.session_state.is_offline = False

# 生成心跳包函数
def generate_heartbeat():
    seq = len(st.session_state.heartbeat_data) + 1
    now = datetime.now()
    st.session_state.heartbeat_data.append({
        "序号": seq,
        "时间": now,
        "时间戳": time.time()
    })
    st.session_state.last_receive_time = time.time()
    st.session_state.is_offline = False

# 掉线检测函数（3秒未收到心跳则判定为掉线）
def check_offline():
    current_time = time.time()
    if current_time - st.session_state.last_receive_time > 3:
        st.session_state.is_offline = True
    else:
        st.session_state.is_offline = False

# 页面标题
st.title("无人机通信心跳监测可视化")

# 操作按钮区
col1, col2 = st.columns(2)
with col1:
    if st.button("发送心跳包"):
        generate_heartbeat()
with col2:
    if st.button("模拟3秒无心跳（触发掉线）"):
        time.sleep(3.1)
        check_offline()

# 实时检测掉线状态
check_offline()

# 状态提示区
if st.session_state.is_offline:
    st.error("⚠️ 警告：无人机已掉线！3秒未收到心跳包！")
else:
    st.success("✅ 状态正常：无人机通信连接稳定")

# 数据可视化区
if st.session_state.heartbeat_data:
    df = pd.DataFrame(st.session_state.heartbeat_data)
    st.subheader("📊 心跳包时序变化折线图")
    st.line_chart(df, x="时间", y="序号")
    st.subheader("📋 原始心跳数据列表")
    st.dataframe(df, use_container_width=True)
