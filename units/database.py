from supabase import create_client, Client
import streamlit as st
import requests
from typing import List, Dict


class SupabaseAuth:
    @staticmethod
    def _init_client() -> Client:
        try:
            supabase_url = st.secrets["supabase_secret"]["url"]
            supabase_key = st.secrets["supabase_secret"]["key"]
            return create_client(supabase_url, supabase_key)
        except Exception as e:
            raise RuntimeError(f"初始化 Supabase 客户端失败：{e}") from e

    def __init__(self):
        self.client: Client = SupabaseAuth._init_client()

    def register(self, email: str, password: str):
        try:
            response = self.client.auth.sign_up({"email": email, "password": password})
            return {"ok": True, "data": response}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def login(self, email: str, password: str):
        try:
            response = self.client.auth.sign_in_with_password({"email": email, "password": password})
            return {"ok": True, "data": response}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def logout(self):
        try:
            response = self.client.auth.sign_out()
            return {"ok": True, "data": response}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        

    def get_user_state(self,access_token,refresh_token)-> Dict:
        try:
            #response = self.client.auth.get_user(jwt= auth_token)
            response  = self.client.auth.set_session(access_token,refresh_token)
            if response.user:
                is_logged_in = True

            return {"ok": True, "data": {"is_logged_in": is_logged_in, "user": response}}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        
    # 其他与用户相关的数据库操作方法可以在这里添加，例如获取用户资料、更新资料等    
    def search_material(self, query: str,limit: int = 3)-> Dict:
        """搜索本地数据库中的素材"""
        try:
            response = self.client.table("assets").select("*", count="exact").ilike("title", f"%{query}%").eq("is_active", True).limit(limit).execute()
            return {"ok": True, "data": response}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    
    
    
    
    def save_resources_to_db(self, resources: List[Dict]) -> Dict:
        """
        将获取到的资源保存到数据库
        
        Args:
            resources: 资源信息列表
            
        Returns:
            保存结果
        """
        try:
            if not resources:
                return {"ok": False, "error": "没有要保存的资源"}
            
            saved_count = 0
            failed_count = 0
            
            for resource in resources:
                try:
                    # 检查是否已存在（根据 original_url 判断）
                    existing = self.client.table("assets").select("id").eq("original_url", resource['original_url']).execute()
                    
                    if existing.data and len(existing.data) > 0:
                        # 已存在则跳过
                        continue
                    
                    # 插入新记录
                    result = self.client.table("assets").insert(resource).execute()
                    if result.data:
                        saved_count += 1
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    st.warning(f"保存单条资源失败：{str(e)}")
                    failed_count += 1
            
            return {
                "ok": True, 
                "message": f"成功保存 {saved_count} 条资源，{failed_count} 条失败",
                "saved_count": saved_count,
                "failed_count": failed_count
            }
            
        except Exception as e:
            st.error(f"批量保存资源失败：{str(e)}")
            return {"ok": False, "error": str(e)}
    
    
    def get_all_categories(self):
        """获取所有素材类别"""
        try:
            response = self.client.table("assets").select("category").eq("is_active", True).distinct().execute()
            categories = [item["category"] for item in response.data if item["category"]]
            return {"ok": True, "data": categories}
        except Exception as e:
            st.error(f"获取素材类别时发生错误：{str(e)}")
            return {"ok": False, "error": str(e)}
        

    
