import streamlit as st
from units.database import SupabaseAuth

from session_state import AppState


class AuthState:
    """认证状态管理类，负责维护用户认证状态、登录/注册/退出逻辑，以及搜索功能的状态。"""
    def __init__(self):
        self.auth = SupabaseAuth()
        AppState.init_session_state()#初始化状态
    @property
    def is_logged_in(self)->str:
        return st.session_state["is_logged_in"]
    @is_logged_in.setter
    def is_logged_in(self, value):
        st.session_state["is_logged_in"] = value

    @property
    def user(self)->str:
        return st.session_state["user"]
    @user.setter
    def user(self, value):
        st.session_state["user"] = value

    @property
    def email(self):
        return st.session_state["email"]
    @email.setter
    def email(self, value):
        st.session_state["email"] = value

    @property
    def status(self):
        return st.session_state["status"]
    @status.setter
    def status(self, value):
        st.session_state["status"] = value

    @property
    def message(self):
        return st.session_state["message"]
    @message.setter
    def message(self, value):
        st.session_state["message"] = value

    @property
    def local_search_results(self):
        return st.session_state["local_search_results"]
    @local_search_results.setter
    def local_search_results(self, value):
        st.session_state["local_search_results"] = value



    def is_authenticated(self):
        if self.user is None or  not self.is_logged_in:
            res = self.auth.get_user_state()
            if res["ok"]:
                is_logged_in = res["data"]["is_logged_in"]
                if is_logged_in:
                    self.user = res["data"]["user"].user
                    self.status = "success"
                    self.is_logged_in = True
                    self.message = f"欢迎回来，{self.user.email}"
            
            else:
                #st.warning(f"当前未登录，正在检查用户状态... {self.status}")
                if self.status == "idle":#初始的默认值
                    return False

                self.status = "error"
                self.message = f"获取用户状态失败：{self.status},{res['error']}"

        return bool(self.user)

    def login(self, email, password):
        if not email or not password:
            self.status = "error"
            self.message = "请输入邮箱和密码"
            return
        self.status = "loading"
        self.message = "正在登录..."
        res = self.auth.login(email, password)
        if res["ok"]:
            user = res["data"]#["user"] #if isinstance(res["data"], dict) else {"email": email}
            self.user = user.user
            self.email = email
            self.status = "success"
            self.message = "登录成功"
            self.is_logged_in = True
            st.rerun()  # 刷新页面以更新状态
        else:
            self.status = "error"
            self.message = f"登录失败：{res['error']}"

    def register(self, email, password):
        if not email or not password:
            self.status = "error"
            self.message = "请输入邮箱和密码"
            return
        self.status = "loading"
        self.message = "正在注册..."
        res = self.auth.register(email, password)
        if res["ok"]:
            self.status = "success"
            self.message = "注册成功，请前往邮箱验证"
            st.rerun()  # 刷新页面以更新状态
        else:
            self.status = "error"
            self.message = f"注册失败：{res['error']}"

    def logout(self):

        if not self.user:
            self.status = "info"
            self.message = "当前未登录"
            return
        res = self.auth.logout()
        if res["ok"]:
            self.user = None
            self.status = "success"
            self.message = "退出登录成功"
            self.is_logged_in = False
            st.rerun()  # 刷新页面以更新状态            
        else:
            self.status = "error"
            self.message = f"退出失败：{res['error']}"

    def search_material(self, query):
            """示例搜索方法，实际实现应根据数据库结构调整"""
            self.status = "loading"
            self.message = f"正在搜索：{query}"
            res = self.auth.search_material(query)
            if res["ok"]:
                self.status = "success"
                self.message = f"搜索完成"
                self.local_search_results = res["data"]
                #st.write("搜索结果：", self.local_search_results)
            else:
                self.status = "error"
                self.message = f"搜索失败：{res['error']}"

    def fetch_external_resources(self, query, source="unsplash", limit=20):
        """示例外部资源获取方法，实际实现应根据数据库结构调整"""
        self.status = "loading"
        self.message = f"正在获取外部资源：{query}"
        res = self.auth.fetch_external_resources(query, source, limit)
        if res["ok"]:
            self.status = "success"
            self.message = f"获取成功"
            self.search_results = res["data"]
            st.write("获取结果：", self.search_results)
        else:
            self.status = "error"
            self.message = f"获取失败：{res['error']}"


    

class AuthSidebar:
    def __init__(self, state: AuthState):
        self.state = state

    def show_loginbar(self):
        with st.sidebar.expander("登录/注册"):
            
            email = st.text_input("邮箱", value=self.state.email, placeholder="example@xx.com")
            #st.text("密码长度需 ≥ 6")
            password = st.text_input("密码", type="password", value="", placeholder="6-20个字符，区分大小写")
            self.state.email = email

            col1, col2 = st.columns([1, 1])
            btn_login = col1.button("登录", use_container_width=True)
            btn_register = col2.button("注册", use_container_width=True)

            if btn_login:
                self.state.login(email, password)
            if btn_register:
                self.state.register(email, password)


    def render(self):
        # st.sidebar.markdown("## 账户认证管理")
        #st.sidebar.title("账户认证管理")
        #st.sidebar.markdown("使⽤ `SupabaseAuth` 进行注册 / 登录 / 退出。")

        if self.state.is_authenticated():
            st.sidebar.success(f"当前已登录：{self.state.user.email}")#get('email', '未知')
            if st.sidebar.button("退出登录", key="logout"):
                self.state.logout()
        else:
            #st.sidebar.info("未登录状态'看看是在哪里出现在的' ")
            self.show_loginbar()

        if self.state.status == "error":
            st.sidebar.error(self.state.message)
        elif self.state.status == "success":
            st.sidebar.success(self.state.message)
        elif self.state.status == "loading":
            st.sidebar.info(self.state.message)
        else:
            st.sidebar.write(f"status:{self.state.status}, 信息：{self.state.message}")
