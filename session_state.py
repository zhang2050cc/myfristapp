import streamlit as st

class AppState:
    def __init__(self):
        # 1. 在这里定义所有状态变量及其默认值
        # 这里可以写复杂的逻辑，比如读取文件、计算默认值等
        self.user_name:     str = "Guest"
        self.user_age:      int = 0
        self.is_logged_in:  bool = False
        self.cart:          list = []  # 普通列表作为默认值

        #AuthState类中的属性
        self.user:      str = None 
        self.session:   str = None #可以存储登录会话信息，如 token 等
        self.email:     str = None   # 可以存储用户的邮箱
        self.status:    str = "idle"  # 可以存储用户状态，如 "idle", "loading", "error" 等
        self.message:   str = None # 可以是字符串或 None
        self.local_search_results: list = []  # 可以是列表或 None

        # MaterialPage 类中的属性
        self.local_search_query:    str = ""
        self.external_search_query: str = ""
        self.external_api_key:      str = ""
        self.current_page:          int = 1
        self.per_page:              int = 15    #self.search_limit:          int = 15
        self.search_source:         str = ""
        #图片方向，orientation
        #self.page:                  int = 1
        #self.orientation:           str = ""

        # MaterialDownLoad 类中的属性
        self.image_data:                list = []
        self.external_search_results:   list = []  # 可以是列表或 None
        

        
       
        






        

    @staticmethod
    def init_session_state():
        """
        静态方法：将 AppState 实例的属性同步到 st.session_state
        """
        # 创建一个临时实例来获取默认值
        # 注意：我们只是用它来读取属性名和默认值，并不保存这个实例
        default_state = AppState()
        
        # 遍历实例的所有属性 (key是变量名, value是默认值)
        for key, value in default_state.__dict__.items():
            if key not in st.session_state:
                st.session_state[key] = value

# # --- 在脚本顶部调用 ---
# AppState.init_session_state()

# # --- 业务逻辑 ---
# st.text_input("姓名", key="user_name")
# st.write(f"当前购物车: {st.session_state.cart}")

# if st.button("添加商品"):
#     st.session_state.cart.append("苹果")
#     st.rerun()