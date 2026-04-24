import streamlit as st
from units.database import SupabaseAuth
from session_state import AppState

#cookies
from streamlit_cookies_manager import EncryptedCookieManager






class AuthState:
    """认证状态管理类，负责维护用户认证状态、登录/注册/退出逻辑，以及搜索功能的状态。"""
    def __init__(self):
        # cookies
        self.cookies = EncryptedCookieManager(password= st.secrets["cookie_password"])
        if not self.cookies.ready():
            st.stop()

        AppState.init_session_state()#初始化状态
        self.auth = SupabaseAuth()

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
        """检查用户是否已登录"""
        try:
            session = self.auth.client.auth.get_session()
            if session:
                #print(f"session: 检查用户是否已登录")
                st.session_state["session"] = session
                self.user = session.user
        except Exception as e:
            print(f"session: {str(e)}")
        

        if self.user is None :
            access_token=self.cookies.get("access_token")
            refresh_token=self.cookies.get("refresh_token")

            if access_token and refresh_token:
                res = self.auth.get_user_state(access_token,refresh_token)
                if res["ok"]:
                    is_logged_in = res["data"]["is_logged_in"]
                    if is_logged_in:
                        self.user = res["data"]["user"].user
                        self.status = "success"
                        self.is_logged_in = True
                        self.message = f"欢迎回来，{self.user.email}"
                
                else:
                    if self.status == "idle":#初始的默认值
                        return False

                    
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
            user = res["data"] # 登录成功返回的响应数据
            self.user = user.user #print(user.json())
            self.email = email
            self.status = "success"
            self.message = "登录成功"
            self.is_logged_in = True

            self.cookies["access_token"]=user.session.access_token
            self.cookies["refresh_token"]=user.session.refresh_token
            self.cookies.save()
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

            self.cookies["access_token"]=""
            self.cookies["refresh_token"]=""
            self.cookies.save()

            # 清空st.session_state
            

            st.rerun()  # 刷新页面以更新状态            
        else:
            self.status = "error"
            self.message = f"退出失败：{res['error']}"
    
    # 用户类别 
    def get_user_category(self):
        """获取用户类别"""
        if not self.user: return ""

        user_id = self.user.id
        user_role = ""
        if user_id: 
            access_token=self.cookies.get("access_token")
            refresh_token=self.cookies.get("refresh_token")
            res = self.auth.get_user_profile(user_id,access_token,refresh_token)
            if res['ok']:
                data = res["data"].data
                if len(data)>0:
                    user_role = data[0]["role"]
                    if user_role == "admin":
                        user_role = "管理员"
                # result: data=[{'role': 'admin'}] count=None
                #print(f"result: {data}")
        return user_role
    
    def search_material(self, query):
        """示例搜索方法，实际实现应根据数据库结构调整"""
        user_role=self.get_user_category()
        print(f"开始搜索：{user_role}")

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
            btn_login = col1.button("登录", width="stretch")
            btn_register = col2.button("注册", width="stretch")

            if btn_login:
                self.state.login(email, password)
            if btn_register:
                self.state.register(email, password)


    def render(self):
        # st.sidebar.markdown("## 账户认证管理")
        #st.sidebar.title("账户认证管理")
        #st.sidebar.markdown("使⽤ `SupabaseAuth` 进行注册 / 登录 / 退出。")

        if self.state.is_authenticated():
            st.sidebar.success(f"已登录{self.state.user.email}")
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
