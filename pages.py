import streamlit as st
from typing import Optional
from datetime import datetime
from units.资源下载类 import MaterialDownLoad
from session_state import AppState
#from units.exceltools import ExcelMerger,LeftJoinStrategy,ConcatenateMerge
import units.exceltools as exceltools
from zoneinfo import ZoneInfo


class BasePage:
    """页面基类：所有页面继承并实现 render()"""
    def __init__(self, auth_state: Optional[object] = None):
        # auth_state 可选注入，页面如需认证信息可以使用
        self.auth_state = auth_state
        AppState.init_session_state()

    def render(self):
        raise NotImplementedError("子类必须实现 render() 方法")


class HomePage(BasePage):
    """首页：总览 + 快捷入口"""
    def render(self):
        self.header(self.auth_state)
        self.body_card()
    
    
    
    
    # ==========================================
    # 🛠️ 工具函数：复制这一段即可，不用看懂内部
    # ==========================================
    def show_colored_text(self,text, color="black", size="32px", align="right"):
        """
        显示彩色大字，无需懂 CSS。
        参数:
            text: 要显示的文字
            color: 颜色 (英文单词如 'red', 'blue', 'orange' 或十六进制 '#FF5733')
            size: 字体大小 (如 '24px', '3rem')
            align: 对齐方式 ('left', 'center', 'right')
        """
        # 内部自动处理 HTML，你只需要关心上面的参数
        html_code = f"""
        <div style="text-align: {align}; font-family: sans-serif; font-weight: bold;">
            <span style="color: {color}; font-size: {size}; font-variant-numeric: tabular-nums;">
                {text}
            </span>
        </div>
        """
        st.markdown(html_code, unsafe_allow_html=True)


    @st.fragment(run_every=1)
    def show_live_clock(self):
        # 获取当前时间（只显示时分秒）纽约时间"America/New_York"  
            
        # 1. 先获取时间对象（不要直接转字符串）
        ny_now = datetime.now(ZoneInfo("Asia/Shanghai"))  #北京时间
        # 2. 获取小时（整数，例如 14）
        hour = ny_now.hour  
        # 3. 获取格式化字符串（例如 "14:30:05"）
        current_time = ny_now.strftime("%H:%M:%S")

        # 根据时间段显示不同的问候
        # 1. 准备问候语
        if 5 <= hour < 12:
            greeting = "☀️ 早上好"
            greet_color = "orange"  # 早上用橙色
        elif 12 <= hour < 18:
            greeting = "🌤️ 下午好"
            greet_color = "#1E88E5"  # 下午用蓝色 (十六进制代码)
        elif 18 <= hour < 22:
            greeting = "🌙 晚上好"
            greet_color = "#8E24AA"  # 晚上用紫色
        else:
            greeting = "😴 夜深了"
            greet_color = "gray"     # 深夜用灰色

        # 显示时间 (大一点，你可以随意改颜色！比如 'red', 'green', '#FF0000')
        # 这里演示改成一种漂亮的深青色
        # 显示问候语 (小一点，彩色)
        
        self.show_colored_text(greeting, color=greet_color, size="14px", align="right")
        self.show_colored_text(current_time, color="#00897B", size="20px", align="right")
        # 使用时间组件显示
        # st.metric(
        #     label=greeting,
        #     value=current_time,
        #     delta=None
        # )

    def header(self, auth_state):
        st.divider()

        # --- 主标题区 ---
        col_title, col_clock_area = st.columns([3, 1])
        with col_title:
            st.markdown("### 🌩️ 云端工具站")
            st.caption("专业 · 简洁 · 有设计感 —— 你的效率加速器")
        with col_clock_area:
            self.show_live_clock()
        st.divider()
    
            
        #     # 用户状态
        #     if auth_state.is_authenticated():
        #         user = auth_state.user
        #         email = getattr(user, "email", None) or (user.get("email") if isinstance(user, dict) else "未知")
        #         username = email.split('@')[0] if '@' in str(email) else email
        #         st.success(f"👤 {username}")
        #     else:
        #         st.info("🚀 未登录")
        
       

    def body_card(self):
                # --- 核心功能卡片区 ---
        st.subheader("🔥 热门功能推荐")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.info("📥 **素材下载**\n\n海量高清图片、图标、模板,一键获取、商用无忧。", icon="🖼️")
            if st.button("去下载 →", key="btn_asset", width="stretch"):
                st.toast("即将跳转到素材库...")

        with col2:
            st.success("💾 **软件下载**\n\n精选免费/开源工具，安全无广告，持续更新。\n\n", icon="📦")
            if st.button("去下载 →", key="btn_soft", width="stretch"):
                st.toast("即将跳转到软件中心...")

        with col3:
            st.warning("🚀 **新功能体验**\n\n抢先试用AI助手、自动化脚本等前沿功能。\n\n", icon="🧪")
            if st.button("去体验 →", key="btn_new", width="stretch"):
                st.toast("即将进入实验室...")

        st.divider()

        # --- 用户数据 & 快速入口 ---
        col_stats, col_action = st.columns([2, 1])

        with col_stats:
            st.metric(label="活跃用户", value="124", delta="+12%")
            st.caption("今日新增用户：8人 | 累计下载次数：3,200+")

        with col_action:
            # 若注入了 auth_state，可展示个性化信息
            if self.auth_state and self.auth_state.is_authenticated():
                user = self.auth_state.user
                email = getattr(user, "email", None) or (user.get("email") if isinstance(user, dict) else "未知")
                
                # 获取用户类别
                user_category = self.auth_state.get_user_category()
                st.markdown(f"###### 👋 :blue[欢迎回来{email}  [{user_category}]]")

            st.button("📊 查看我的统计", width="stretch", key="btn_stats")
            st.button("⚙️ 设置偏好", width="stretch", key="btn_settings")
        st.info("🌀 正在加载最新资源...", icon="🔄")
        st.divider()

        # --- 底部提示 & 版权 ---
        st.info("💡 提示：侧边栏用于登录/注册，主区为业务页面。所有数据实时同步，请放心使用。", icon="ℹ️")

        st.markdown("""
        <div style="text-align: center; color: #888; font-size: 14px; margin-top: 20px;">
            Made with ❤️ using <b>Streamlit</b> + <b>Supabase</b>
        </div>
        """, unsafe_allow_html=True)

    
class MaterialPage(BasePage):
    """素材下载页：示例列表"""
    def __init__(self, auth_state = None):
        super().__init__(auth_state)
        self.material_downloader = MaterialDownLoad(auth_state)
        
        #要展示的素材列表的键的名称
        self.material_list_key = ["thumbnail_url","image_url","resolution","file_size"]
        #搜索条件local_search_query ,search_source ,apikey,size_option #图片方向，orientation
    @property
    def orientation(self):
        return st.session_state["orientation"]  
    @orientation.setter
    def orientation(self,value):
        st.session_state["orientation"] = value

    @property
    def size_option(self):
        return st.session_state["size_option"]
    # @size_option.setter
    # def size_option(self,value):
    #     st.session_state["size_option"] = value  

    @property
    def search_source(self):
        return st.session_state["search_source"]
    @search_source.setter
    def search_source(self,value):
        st.session_state["search_source"] = value

    @property
    def local_search_query(self):
        return st.session_state["local_search_query"]
    @local_search_query.setter
    def local_search_query(self,value):
        st.session_state["local_search_query"] = value

    @property
    def external_search_query(self):
        return st.session_state["external_search_query"]
    @external_search_query.setter
    def external_search_query(self,value):
        st.session_state["external_search_query"] = value
    @property
    def external_api_key(self):
        return st.session_state["external_api_key"]
    @external_api_key.setter
    def external_api_key(self,value):
        st.session_state["external_api_key"] = value    

    @property
    def current_page(self):
        return st.session_state["current_page"]
    @current_page.setter
    def current_page(self,value):
        st.session_state["current_page"]=value

    @property
    def per_page(self):
        """limit"""
        return st.session_state["per_page"]
    @per_page.setter
    def per_page(self,value):
        """limit"""
        st.session_state["per_page"]=value

    
    # 获取key[Pixabay][Pexels][Unsplash]
    def get_key(self,source):
        """获取key"""
        
        source = source.lower()
        key = ""
        user_name = self.auth_state.get_user_category()
        print(f"获取key:{source}_user_name:{user_name}")
        if user_name == "管理员":
            st.session_state["user_name"] = user_name
            match source:
                case "pixabay":
                    key = st.secrets["Pixabay"]["key"]
                case "pexels":
                    key = st.secrets["Pexels"]["key"]
                    #print(f"获取key:{source}_key:{key}")
                case "unsplash":
                    key = st.secrets["Unsplash"]["key"]
        return key        
        



    #所有的当前页面渲染都在render()方法中进行调用
    def render(self):
        """渲染素材下载页面的内容"""
        tab1, tab2 = st.tabs(["🔍 本地素材库", "🌐 获取外部资源"])
        with tab1:
            #渲染本地素材 搜索框 button
            self.render_local_search_material()  
            self.render_local_search_results()
        with tab2:
            self.render_external_resource_fetcher()
            self.render_external_search_results() #展示素材网
    

    #渲染搜索结果用列表展示本地数据库中的素材 self.search_query and self.auth_state and 
    def render_local_search_results(self):
        """
        没有搜索结果时，显示推荐素材或热门素材
        搜索结果时，显示搜索结果
        """
        
        if hasattr(self.auth_state, 'local_search_results'):
            results = getattr(self.auth_state, 'local_search_results')
                
            if results:
                st.write(f"本地搜索结果：'{self.local_search_query}' 共找到{results.count} 个结果")
                
                #st.write(results)
                #st.table(results.data)# 搜索结果用列表展示
                if results.count > 0:
                    new_tabledata =[
                        {key:item.get(key) for key in self.material_list_key} 
                        for item in results.data if isinstance(results.data, list)
                    ]
                    st.table(new_tabledata)
                   
            
            else:
                # 显示推荐素材或热门素材
                st.markdown("- *`热门素材`*")
                st.table([
                    {"名称": "图片素材 A", "类型": "PNG", "来源": "本地", "操作": "查看"},
                    {"名称": "图标包 B", "类型": "SVG", "来源": "本地", "操作": "查看"},
                    {"名称": "模板 C", "类型": "PSD", "来源": "本地", "操作": "查看"},
                ])   
    
    
    #渲染本地搜索素材输入框 和按钮
    def render_local_search_material(self):
        """渲染本地搜索素材输入框 和按钮"""
        with st.form(key="local_search_form", clear_on_submit=False):
            col1, col2 = st.columns([4, 1])
            with col1:
                query = st.text_input("🔍 搜索本地素材",value = self.local_search_query,
                                    placeholder="输入关键词...", label_visibility="collapsed")
            with col2:
                submitted = st.form_submit_button("搜索", width="stretch")
                #去除首尾空格后再搜索
        if submitted:
            clean_query = query.strip()
            if clean_query and self.auth_state:
                self.local_search_query = clean_query
                self.auth_state.search_material(self.local_search_query)
        st.markdown("---") 
            

    def render_external_search_results(self):
        if hasattr(self.material_downloader,"search_result"): 
            data = getattr(self.material_downloader,"search_result",None)#搜索的结果
           
            if data :
                #st.write(f"开始渲染了.....{self.search_source}")
                #st.json(data)
                photo_info = self.material_downloader.GetUrlBySearchResults(data,self.search_source)
                if not photo_info["photos"]:
                    st.caption(f"没有搜索到内容：正在使用{self.search_source} | 搜索 {self.external_search_query} | 图片方向 {self.orientation} | 图片预览尺寸 {self.size_option} 第页数量 {self.per_page}")
                    return #字典中photos字段为空列表，没有图片数据
                
                #page     = photo_info["page"]
                #per_page = photo_info["per_page"]
                photos   = photo_info["photos"]
                total_results = photo_info["total_results"]
                

                #st.write(f"total_results= {total_results}, per_page = {self.per_page} ,photos={len(photos)}" )

                
                newpage = self.current_page

                # 显示结果统计  # 公式：(总数 + 每页数量 - 1) // 每页数量
                total_pages=(total_results + self.per_page - 1 ) // self.per_page
                st.caption(f"正在使用{self.search_source} | 搜索 {self.external_search_query} | 图片方向 {self.orientation} | 图片预览尺寸 {self.size_option}  | 共找到 {total_results} 张图片 | 当前第 {self.current_page} / {total_pages} 页")


                # 获取图片信息 3列显示
                cols = st.columns(3)
                for index, photo in enumerate(photos):#下标从0开始
                    with cols[index % 3]:#0.1.2
                        # 安全获取图片链接
                        ImageUrls = self.material_downloader.extract_image_urls(photo,self.size_option,self.search_source)

                        image_url = ImageUrls["image_url"]#: None,          # 页面展示用
                        download_url = ImageUrls["download_url"]#: None,       # 下载用
                        original_image_url = ImageUrls["original_image_url"]#: None, # 原图链接
                        photographer = ImageUrls["photographer"]#: None        # 摄影师信息


                        # src_dict = photo.get("src", {})
                        # img_url = src_dict.get(self.size_option, src_dict.get("medium", ""))
                        # original_url= src_dict.get("original",src_dict.get("large2x",src_dict.get("large","")))
                        # photographer = photo.get("photographer", "Unknown")#摄影师
                        # p_url = photo.get("url", "#")#原图链接


                        
                        if image_url:# 图片信息

                            with st.spinner("🔄 加载中..."):
                                st.image(image_url, width="stretch")#显示图片
                                st.caption(f"📸: {photographer}")

                                # 渲染两个按钮(查看原图,下载此图)同一行显示
                                columns = st.columns(2)
                                with columns[0]:
                                    st.link_button("🔗 查看原图", original_image_url, width="stretch")# 使用链接按钮
                                with columns[1]:
                                    if st.button("⬇️ 下载此图", key=f"download_{index}_{photo['id']}"):
                                        #img_data = requests.get(img_url).content
                                        self.material_downloader.ImageDwon(download_url)
                                        file_name = f"{photographer}_{photo['id']}.jpg"
                                        st.download_button(
                                            label       ="✅ 下载成功 (点击保存)",
                                            data        = getattr(self.material_downloader,"image_data"),# self.material_downloader.image_data,
                                            file_name   = file_name,
                                            mime        = "image/jpeg",
                                            key         = f"dl_btn_{index}_{photo['id']}" # 给下载按钮也加个唯一 key
                                        )
                                    

                # --- 分页控制器 ---
                st.divider()
                col_prev, col_info, col_next = st.columns([1, 2, 1])
                with col_prev:
                    if st.button("⬅️ 上一页", disabled=(self.current_page <= 1), width="stretch"):# use_container_width=True,
                        newpage = self.current_page - 1

                with col_info:
                    # st.write(f"**页码**: {self.current_page} / {total_results}")
                    st.markdown(
                                f"""
                                <div style="text-align: center; font-size: 16px; font-weight: 500; padding-top: 10px;">
                                    页码 <span style="color:#FF4B4B; font-size: 18px;">{self.current_page}</span> / {total_pages}
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                with col_next:#if not next_page.s
                    if st.button("➡️ 下一页", disabled=(self.current_page >= total_pages), width="stretch"):#page >= total_results
                        newpage = self.current_page + 1
                
                    
                if self.current_page != newpage:
                    self.current_page = newpage

                    self.material_downloader.search_material(
                        self.external_search_query,
                        self.search_source,
                        self.external_api_key,
                        self.per_page,
                        current_page = self.current_page,
                        direction=self.orientation
                        )   
                    st.rerun()           

   
    def render_external_resource_fetcher(self):
        """渲染外部资源获取界面"""
        # --- 1. 使用 st.form 包裹所有输入控件 ---
        # 这样用户修改下拉框或数字时，页面不会疯狂刷新，只有点搜索才运行
        with st.form(key="search_form", clear_on_submit=False):
            # --- 第一行：核心搜索区 (使用 columns 分列) ---
            # 
            #with col_keyword:
            search_query = st.text_input(
                "搜索关键词", 
                placeholder="🔍 搜索关键词",
                value= self.external_search_query,
                label_visibility="collapsed" # 隐藏标签，让界面更干净
            )
                
            
               
            # --- 第二行：高级设置 (默认折叠，保持界面整洁) ---
            with st.expander("⚙️ 高级设置 (API Key & 说明)", expanded=False):
                col_source, col_ori, col_size,col_count = st.columns([1.2, 1, 1, 0.8])

                with col_source:
                    source = st.selectbox(
                        "选择资源来源",
                        ["pexels", "unsplash", "pixabay"],
                        label_visibility="collapsed",
                        key="source_option", # 建议也给这个加上 key，防止刷新重置
                        #format_func=lambda x: f"📷 {x.capitalize()}" if x == "unsplash" else (f"🎨 {x.capitalize()}" if x == "pexels" else f"🖼️ {x.capitalize()}")
                        # 使用字典映射，代码可读性更强
                        format_func=lambda x: {
                            "unsplash": "📷 Unsplash",
                            "pexels":   "🎨 Pexels",
                            "pixabay":  "🖼️ Pixabay"
                        }[x]
                    )

                with col_size:
                    st.selectbox(
                        "图片预览尺寸",
                        ["thumbnail", "small", "medium", "large", "large2x", "original"],
                        index=2,
                        label_visibility="collapsed",
                        key="size_option", # 建议也给这个加上 key，防止刷新重置
                        format_func=lambda x:{
                            "thumbnail": "缩略图",
                            "small": "小图",
                            "medium": "中图",
                            "large": "大图",
                            "large2x": "超大图",
                            "original": "原图"
                        }[x]
                    )

                with col_ori:    #图片方向，orientation 可选值：landscape (横向), portrait (纵向), square (方形)
                    # 1. 定义一个字典，键是显示给用户的，值是程序内部使用的
                    ORIENTATION_MAP = {
                        "不限": "",
                        "横向": "landscape" ,
                        "纵向": "portrait" ,
                        "方形": "square",
                    }
                    # 2. 使用字典的键作为下拉框的选项
                    selected_label = st.selectbox(
                        "图片方向",
                        options=list(ORIENTATION_MAP.keys()), # 显示: ["不限", "横向", "纵向", "方形"]
                        index=1,                              # 默认选中 "横向"
                        label_visibility="collapsed",
                        #key="orientation"
                    )
                    # 3. 通过选中的键，从字典中获取对应的程序值
                    selected_label = ORIENTATION_MAP[selected_label]
                    
                    # st.selectbox(
                    #     "图片方向",
                    #     ["", "landscape", "portrait", "square"],#Accepted values: "all", "horizontal", "vertical"
                    #     index = 1,
                    #     label_visibility="collapsed",
                    #     key="orientation" ,# 建议也给这个加上 key，防止刷新重置
                    #     # 使用 format_func 将内部值映射为友好的中文显示
                    #     format_func=lambda x: {
                    #         "":          "不限",       # 对应 API 不传或空值
                    #         "landscape": "横向", 
                    #         "portrait":  "纵向", 
                    #         "square":    "方形"
                    #     }.get(x, x)
                    # )

                with col_count:
                    #limit = st.number_input("数量", min_value=5, max_value=30, value=10, step=1,label_visibility="collapsed")
                    limit = st.number_input(
                                            "数量",
                                            min_value=5,
                                            max_value=30,
                                            value=15,
                                            step=1,
                                            label_visibility="collapsed",
                                            help="请输入图片数量（5-30张）"
                                        )

                c1, c2 = st.columns(2)

                with c1:
                    apikey = st.text_input("API Key", 
                                            value = "" if st.session_state["user_name"]=="管理员" else self.external_api_key, 
                                            label_visibility="collapsed",
                                            placeholder=f"粘贴你的{self.search_source}密钥...", 
                                            type = "password")
                    st.markdown("""
                    - 💡 获取 API Key：[Unsplash](https://unsplash.com/developers) | [Pexels](https://www.pexels.com/api/) | [Pixabay](https://pixabay.com/zh/service/about/api/)
                    - 💡 提示：支持中文搜索
                    - ⚠️ 注意：使用前需要配置对应网站的APIKey   
                    """)
                    
                    
                with c2:
                    st.markdown("""
                    *支持的资源网站*:
                    - 📷 Unsplash - 高质量摄影图片
                    - 🎨 Pexels - 免费图片和视频
                    - 🖼️ Pixabay - 超过 200 万张免费图片
                    """)
                    
             # --- 第三行：巨大的搜索按钮 ---
            # form_submit_button 必须在 form 内部
            submitted = st.form_submit_button("🚀 开始搜索外部资源", width="stretch", type="primary")       
            if submitted:
                
                query = search_query.strip()
                apikey= apikey.strip()
                if not apikey: 
                    apikey = self.get_key(source)
                    if not apikey:
                        self.auth_state.message = "请输入API Key"   
                        self.auth_state.status = "error"
                        st.rerun()
                        #print("请输入API Key")

                if source == "pixabay":#"horizontal", "vertical"
                    if selected_label == "landscape":#landscape (横向), portrait (纵向)
                        selected_label ="horizontal"
                    if selected_label == "portrait":
                        selected_label ="vertical"

                if query and apikey:
                    #st.toast("开始下载")
                    self.search_source          = source
                    self.external_api_key       = apikey 
                    self.external_search_query  = query
                    self.per_page               = limit
                    self.current_page = 1
                    self.orientation = selected_label
                    #st.caption(f"图片尺寸：{self.size_option}， 方向: {self.orientation},每页数量: {self.per_page},搜索源: {self.search_source}")
                    self.material_downloader.search_material(query, source, apikey, limit, direction=self.orientation)
                    

                
                
                
        
        
        
        
        
        # # 搜索按钮
        # if st.button("🔍 搜索外部资源", use_container_width=True):
        #     if search_query and self.auth_state:
        #         with st.spinner(f"正在从 {source} 搜索 '{search_query}'..."):
        #             # 调用外部资源获取 API
        #             self.auth_state.fetch_external_resources(
        #                 query=search_query,
        #                 source=source,
        #                 limit=limit
        #             )
                    
        #             result = self.auth_state.search_results
        #             if result:
        #                 resources = result
        #                 st.success(f"✅ 找到 {len(resources)} 条资源")
                        
        #                 # 存储到 session state 以便后续批量导入
        #                 st.session_state['external_resources'] = resources
                        
        #                 # 展示搜索结果预览
        #                 st.subheader("搜索结果预览")
                        
        #                 # 使用卡片式布局展示
        #                 for i, item in enumerate(resources):
        #                     with st.expander(f"📄 {item.get('title', '无标题')} - {item.get('author', '未知作者')}"):
        #                         col_img, col_info = st.columns([1, 2])
                                
        #                         with col_img:
        #                             # 显示缩略图
        #                             thumbnail = item.get('thumbnail_url', '')
        #                             if thumbnail:
        #                                 st.image(thumbnail, use_column_width=True)
                                
        #                         with col_info:
        #                             st.write(f"**描述**: {item.get('description', '暂无描述')}")
        #                             st.write(f"**类别**: {item.get('category', '未分类')}")
        #                             st.write(f"**来源**: {item.get('source', '未知')}")
        #                             st.write(f"**作者**: {item.get('author', '未知')}")
        #                             st.write(f"**许可证**: {item.get('license_type', '未知')}")
                                    
        #                             # 标签
        #                             tags = item.get('tags', [])
        #                             if tags:
        #                                 st.write(f"**标签**: {', '.join(tags) if isinstance(tags, list) else tags}")
                                    
        #                             # 链接
        #                             original_url = item.get('original_url', '#')
        #                             download_link = item.get('download_link', '#')
        #                             st.markdown(f"[🔗 查看原图]({original_url}) | [⬇️ 下载链接]({download_link})")
                        
        #                 # 批量导入按钮
        #                 st.markdown("---")
        #                 col_btn1, col_btn2 = st.columns([1, 3])
        #                 with col_btn1:
        #                     if st.button("💾 批量导入到数据库", type="primary", use_container_width=True):
        #                         with st.spinner("正在保存到数据库..."):
        #                             save_result = self.auth_state.save_resources_to_db(resources)
                                    
        #                             if save_result["ok"]:
        #                                 st.success(f"✅ {save_result['message']}")
        #                                 st.rerun()
        #                             else:
        #                                 st.error(f"❌ 保存失败：{save_result.get('error', '未知错误')}")
                        
        #             else:
        #                 st.error(f"❌ 搜索失败：")
        #     else:
        #         st.warning("请输入搜索关键词")
        
        # # 使用说明
        # with st.expander("📖 使用说明"):
            # st.markdown("""
            # ### 如何获取 API Key？
            
            # #### Unsplash
            # 1. 访问 https://unsplash.com/developers
            # 2. 注册并创建应用
            # 3. 获取 Access Key
            # 4. 在 `units/database.py` 中替换 `YOUR_UNSPLASH_ACCESS_KEY`
            
            # #### Pexels
            # 1. 访问 https://www.pexels.com/api/
            # 2. 注册并申请 API Key
            # 3. 在 `units/database.py` 中替换 `YOUR_PEXELS_API_KEY`
            
            # #### Pixabay
            # 1. 访问 https://pixabay.com/api/docs/
            # 2. 注册并获取 API Key
            # 3. 在 `units/database.py` 中替换 `YOUR_PIXABAY_API_KEY`
            
            # ### 注意事项
            # - 每个 API 都有调用频率限制，请合理使用
            # - 保存的只是图片的链接信息，不是图片文件本身
            # - 使用时请遵守各网站的许可协议
            # """)
               


class SoftwarePage(BasePage):
    """软件下载页"""
    def __init__(self, auth_state = None):
        super().__init__(auth_state)
        self.auth_state = auth_state

        
        # 合并方式 1. 左外连接
        self.strategy = exceltools.LeftJoinStrategy()
        self.mergertool = exceltools.ExcelMerger()



    def render(self):
        # --- Streamlit 交互界面 ---
        st.header("🛠️ 可扩展 Excel 合并工具")
        st.markdown("支持多种合并方式，未来可轻松扩展新功能！")
        # st.header("软件下载")
        # st.markdown("在此处展示软件发布版本与下载链接。")
        st.expander("版本 v1.2.0 说明", expanded=False).write("修复若干 bug，性能优化。")
        self.display_page()

    # ---界面: 1.上传文件（主表、待合并表）2.选择合并方式3.执行合并4.下载结果5.保存结果
    def display_page(self):
        cols = st.columns([1, 1])
        with cols[0]:
            file1= st.file_uploader("上传主表", 
                             type=["xlsx", "xls", "csv"], 
                             accept_multiple_files=False,
                             key="main_file"
                             )
        with cols[1]:
            file2= st.file_uploader("上传待合并表", 
                             type=["xlsx", "xls", "csv"], 
                             accept_multiple_files=False,
                             key="merge_files"
                             )

        if file1 and file2:
            try:
                # 2. 选择合并方式
                merge_type = st.radio(
                    "选择合并方式：",
                    options=["left_join", "concatenate"],
                    format_func=lambda x: "左右合并（按共同列匹配）" if x == "left_join" else "上下合并（行追加）"
                )

                # 3. 初始化合并器    
                if merge_type == "left_join":
                    df1_temp = self.mergertool.read_file(file1)
                    df2_temp = self.mergertool.read_file(file2)

                    #df1_temp = pd.read_excel(file1) #if file1.name.endswith('.xlsx') else pd.read_csv(file1)
                    #df2_temp = pd.read_excel(file2) #if file2.name.endswith('.xlsx') else pd.read_csv(file2)
                    common_cols = list(set(df1_temp.columns) & set(df2_temp.columns))

                    if not common_cols:
                        st.error("❌ 两个表没有共同的列名，无法进行左右合并！")
                        st.info("请检查两个表是否都包含相同的列名。")
                    else:
                        join_col = st.selectbox("选择合并依据列：", common_cols)
                        self.mergertool.set_strategy(self.strategy)
                        merged_df = self.mergertool.execute_merge(file1, file2, on_col=join_col)

                        #strategy = LeftJoinMerge()
                        #merger = ExcelMerger(strategy)
                        #merged_df = merger.execute_merge(file1, file2, on_col=join_col)
                if merge_type == "concatenate":
                    strategy = exceltools.ConcatenateMerge()
                    self.mergertool.set_strategy(strategy)
                    merged_df = self.mergertool.execute_merge(file1, file2)
                
                else:  # concatenate
                    pass  
                
                # 4. 显示合并结果
                st.subheader("合并结果：")
                st.dataframe(merged_df)

                # 5. 下载结果
                result_bytes = self.mergertool.to_excel_bytes(merged_df)
                st.download_button(
                    label="📥 下载合并结果 Excel",
                    data=result_bytes,
                    file_name="merged_result.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )      
                
                 
            except Exception as e:
                st.error(f"❌ 处理过程中发生错误：{e}")

        
        



class FeaturesPage(BasePage):
    """新功能展示页"""
    def render(self):
        st.header("新功能展示")
        st.markdown("本页用于展示新功能、演示 GIF 或视频。")
        st.info("示例：登录后可以看到个性化新功能提示。")
        if self.auth_state and self.auth_state.is_authenticated():
            st.success("您已登录，可体验完整功能。")
