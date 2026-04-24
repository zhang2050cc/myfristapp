
import sys, os
# 将项目根目录加入模块搜索路径（根据实际路径调整两级上层）
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, proj_root)


import streamlit as st
from units.sidebar import AuthState, AuthSidebar
import time
from datetime import datetime

def header(area_title: str, auth_state: AuthState):
    # 顶部大标题 + 简短说明 + 当前登录状态卡片
    left, right = st.columns([3, 1])
    with left:
        
        st.title("*`云端工具站 · 管理控制台`*")
        st.markdown("集成 Supabase `SupabaseAuth` `认证与工具面板` — 专业、简洁、有设计感。")
    with right:
        st.metric("当前时间", datetime.now().strftime("%H:%M:%S"),border=True,width="content")

        if auth_state.is_authenticated():
            # 兼容 user 为对象或字典
            user = auth_state.user
            email = getattr(user, "email", None) or (user.get("email") if isinstance(user, dict) else "未知")
            st.success(f"已登录：{email}")
        else:
            st.info("未登录")

        
        

def home_page(auth_state: AuthState):
    header("控制台", auth_state)

    #st.header("欢迎页")
    #st.markdown("这里是平台总览与快速入口。下方为常用操作卡片。")
    

    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("认证状态")
        st.write("状态：", auth_state.status)
        st.write("提示：", auth_state.message)
    with c2:
        st.subheader("快速操作")
        if st.button("刷新状态"):
            st.rerun()
        st.button("触发示例任务")
    with c3:
        st.subheader("帮助")
        st.info("侧边栏用于登录/注册/退出。主区展示业务内容。")

    st.markdown("---")
    st.subheader("最近活动（示例）")
    st.table([
        {"时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "事件": "页面打开"},
        {"时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "事件": "认证模块就绪"},
        {"时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "事件": "页面打开"},
        {"时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "事件": "认证模块就绪"},
    ])

def material_page():
    st.header("素材下载")
    st.markdown("示例：在这里放素材列表、预览与下载按钮。")
    st.info("这是一个占位页，你可以把实际素材列表放在这里。")

def software_page():
    st.header("软件下载")
    st.markdown("示例：提供软件下载链接、版本说明和安装指南。")

def new_features_page():
    st.header("新功能展示")
    st.markdown("在此处展示最新迭代、功能说明和演示视频/动图等。")
    st.success("演示：登录后主区会显示用户信息卡片（更沉浸的体验）")
    st.markdown("- 列表项 1\n- 列表项 2")
    st.text("#颜色：使用 :颜色[文本内容] 的语法。") 
    st.code("#表情：使用 :emoji_name: 的语法。")
    st.markdown(">这是 :red[红色文本]，这是 :blue-background[蓝色文本] 且 **:blue[加粗]**。")
    st.markdown("- 今天心情不错 :sunglasses: :heart:")





def main():
    st.set_page_config(page_title="Supabase Auth 专业版", layout="wide")
    # 初始化认证状态与侧栏
    auth_state = AuthState()
    auth_sidebar = AuthSidebar(auth_state)
    auth_sidebar.render()  # 侧边栏渲染（登录/注册/退出）

    # 顶部头部区域
    #header("控制台", auth_state)

    # 页面主导航区（tabs）
    tabs = st.tabs(["🏠 首页", "📊 素材下载", "📑 软件下载", "⚙️ 新功能展示", "👥 关于"])
    with tabs[0]:
        home_page(auth_state)
    with tabs[1]:
        material_page()
    with tabs[2]:
        software_page()
    with tabs[3]:
        new_features_page()
    with tabs[4]:
        st.header("关于")
        st.markdown("这是一个演示型控制台页面，展示页面排版与认证集成方案。")

    # 页脚
    st.divider()

    APP_NAME="云端工具站"
    APP_VERSION="v1.0.0"
    st.caption(f"""
    © 2026 {APP_NAME} | 版本：{APP_VERSION} | 
    [使用条款](#) | [隐私政策](#) | [联系我们](#)
    """)



if __name__ == "__main__":
    main()