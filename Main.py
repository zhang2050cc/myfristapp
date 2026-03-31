import streamlit as st
from units.sidebar import AuthState, AuthSidebar
from pages import HomePage, MaterialPage, SoftwarePage, FeaturesPage





def main():
    # 设置页面配置，包括背景主题
    st.set_page_config(
        page_title="云端工具站", 
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 使用 Streamlit 的主题配置（简单改变配色）
    # st.markdown("""
    # <style>
    # [data-testid="stApp"] {
    #     background-color: #f0f2f6;
    # }
    # </style>
    # """, unsafe_allow_html=True)
    
    # 初始化认证状态与侧栏
    auth_state = AuthState()
    AuthSidebar(auth_state).render()

    # 渲染头部
    
    
    # 页面类实例
    pages = [
        ("🏠 首页", HomePage(auth_state)),
        ("📦 素材下载", MaterialPage(auth_state)),
        ("💻 软件下载", SoftwarePage(auth_state)),
        ("✨ 新功能", FeaturesPage(auth_state)),
    ]

    # 使用 st.tabs 渲染每个页面
    tab_objs = st.tabs([p[0] for p in pages])
    for tab, (_, page_instance) in zip(tab_objs, pages):
        with tab:
            page_instance.render()



   



    # 2. 提取选项列表供 segmented_control 使用
    #options = [p[0] for p in pages]

    # # 3. 创建分段控制器
    # # label_visibility="collapsed" 隐藏标题，让界面更干净
    # selected_label = st.segmented_control(
    #     "导航菜单", 
    #     options, 
    #     default=options[0], # 默认选中第一个
    #     label_visibility="collapsed"
    # )

    # # 4. 根据选中的值，动态渲染对应的页面
    # # 构建一个映射字典，方便通过标签名找到实例
    # page_map = {label: instance for label, instance in pages}

    # # 获取当前选中的页面实例
    # current_page_instance = page_map.get(selected_label)

    # if current_page_instance:
    #     # 只有当前选中的页面会被渲染和执行
    #     current_page_instance.render()
    # else:
    #     st.error("❌ 页面未找到")



    # 底部信息
    # st.caption("💡 提示：侧边栏用于认证，主区为业务页面")
    # st.caption("Made with ❤️ using Streamlit + Supabase")


if __name__ == "__main__":
    main()