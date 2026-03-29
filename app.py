import streamlit as st
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="无人机航线规划系统",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 全局状态
if "drone_data" not in st.session_state:
    st.session_state.drone_data = {
        "point_a": {"lat": 32.2322, "lng": 118.749, "set": False},
        "point_b": {"lat": 32.2343, "lng": 118.749, "set": False},
        "height": 50,
        "heartbeat": []
    }

# ==================== WGS84 转 GCJ02（Python 原生，无需安装库）====================
def wgs84_to_gcj02(lat, lng):
    a = 6378245.0
    ee = 0.00669342162962963
    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * 3.14159265358979323846
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * 3.14159265358979323846 / 180.0)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * 3.14159265358979323846 / 180.0)
    return lat + dlat, lng + dlng

def transform_lat(x, y):
    return -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))

def transform_lng(x, y):
    return 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))

import math

# 侧边栏
with st.sidebar:
    st.title("无人机系统")
    page = st.radio("功能页面", ["航线规划", "飞行监控"], key="page")
    st.divider()

    st.subheader("坐标系设置")
    coord_system = st.radio("输入坐标系", ["GCJ-02(高德/百度)", "WGS-84"], index=0, key="coord")
    st.divider()

    st.subheader("系统状态")
    st.write(f"A点已设：{'✅' if st.session_state.drone_data['point_a']['set'] else '❌'}")
    st.write(f"B点已设：{'✅' if st.session_state.drone_data['point_b']['set'] else '❌'}")

# ====================== 航线规划 ======================
if page == "航线规划":
    st.title("🗺️ 航线规划")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("起点A")
        a_lat = st.number_input("纬度", value=st.session_state.drone_data["point_a"]["lat"], format="%.6f", key="a_lat")
        a_lng = st.number_input("经度", value=st.session_state.drone_data["point_a"]["lng"], format="%.6f", key="a_lng")
        if st.button("设置A点", type="primary", key="set_a"):
            lat, lng = a_lat, a_lng
            if coord_system == "WGS-84":
                lat, lng = wgs84_to_gcj02(lat, lng)
            st.session_state.drone_data["point_a"] = {"lat": lat, "lng": lng, "set": True}
            st.success("✅ A点设置成功！")

    with col2:
        st.subheader("终点B")
        b_lat = st.number_input("纬度", value=st.session_state.drone_data["point_b"]["lat"], format="%.6f", key="b_lat")
        b_lng = st.number_input("经度", value=st.session_state.drone_data["point_b"]["lng"], format="%.6f", key="b_lng")
        if st.button("设置B点", type="primary", key="set_b"):
            lat, lng = b_lat, b_lng
            if coord_system == "WGS-84":
                lat, lng = wgs84_to_gcj02(lat, lng)
            st.session_state.drone_data["point_b"] = {"lat": lat, "lng": lng, "set": True}
            st.success("✅ B点设置成功！")

    st.divider()
    st.subheader("飞行参数")
    height = st.slider("设定飞行高度(m)", 10, 200, st.session_state.drone_data["height"], key="height")
    st.session_state.drone_data["height"] = height
    st.info(f"当前设定高度：{height}m")

    st.divider()
    st.subheader("当前航线信息")
    st.json({
        "起点A": st.session_state.drone_data["point_a"],
        "终点B": st.session_state.drone_data["point_b"],
        "飞行高度": st.session_state.drone_data["height"]
    })

# ====================== 飞行监控 ======================
if page == "飞行监控":
    st.title("✈️ 飞行监控（心跳包）")
    st.divider()

    if st.button("上传测试心跳包", type="primary", key="upload_heartbeat"):
        heartbeat = {
            "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "纬度": st.session_state.drone_data["point_a"]["lat"] + 0.0001,
            "经度": st.session_state.drone_data["point_a"]["lng"] + 0.0001,
            "高度": st.session_state.drone_data["height"],
            "状态": "正常"
        }
        st.session_state.drone_data["heartbeat"].append(heartbeat)
        if len(st.session_state.drone_data["heartbeat"]) > 100:
            st.session_state.drone_data["heartbeat"] = st.session_state.drone_data["heartbeat"][-100:]
        st.success("✅ 测试心跳包上传成功！")

    st.divider()
    st.subheader("心跳包历史数据")

    if st.session_state.drone_data["heartbeat"]:
        st.dataframe(st.session_state.drone_data["heartbeat"], use_container_width=True)
    else:
        st.info("暂无心跳包数据")

    if st.button("清空历史数据", type="secondary", key="clear"):
        st.session_state.drone_data["heartbeat"] = []
        st.success("✅ 已清空历史数据")
