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
        

    def get_user_state(self)-> Dict:
        try:
            response = self.client.auth.get_user()
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
    
    
    def fetch_external_resources(self, query: str, source: str = "unsplash", limit: int = 20) -> Dict:
        """
        从外部免费资源网站搜索并获取下载链接
        
        Args:
            query: 搜索关键词
            source: 资源来源 (unsplash, pexels, pixabay)
            limit: 返回结果数量
            
        Returns:
            包含资源信息的字典列表
        """
        try:
            resources = []
            
            if source == "unsplash":
                # Unsplash API
                url = f"https://api.unsplash.com/search/photos"
                params = {
                    "query": query,
                    "per_page": min(limit, 30),
                    "client_id": st.secrets.get("external_api", {}).get("unsplash_key", "YOUR_UNSPLASH_ACCESS_KEY")
                }
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("results", []):
                        resources.append({
                            "title": f"{item.get('description', '无标题')[:50]} - {item['user']['name']}",
                            "description": item.get('description', '暂无描述') or f"由 {item['user']['name']} 上传的精美图片",
                            "category": "摄影",
                            "image_url": item['urls']['full'],
                            "thumbnail_url": item['urls']['small'],
                            "download_link": item['links']['download'],
                            "source": "Unsplash",
                            "author": item['user']['name'],
                            "license_type": "Unsplash License",
                            "original_url": item['links']['html'],
                            "tags": [tag['title'] for tag in item.get('tags', [])][:5] if isinstance(item.get('tags'), list) else [],
                            "is_active": True
                        })
                        
            elif source == "pexels":
                # Pexels API
                url = f"https://api.pexels.com/v1/search"
                #url = "https://api.pexels.com/v1/search"
                headers = {
                    
                    #"Authorization": st.secrets.get("external_api", {}).get("pexels_key", "YOUR_PEXELS_API_KEY"),
                    "Authorization":"gypVRvEnHxTyKza3lkw5AddI2fI1FhWAxIQRdctdP72IFZ6ELBuiA2Ux",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                params = {"query": query, 
                           "per_page":min(limit, 30),
                            "size": "large",          # 🔑 关键：只搜大图 (通常 > 1920px)
                            "orientation": "landscape" # 🔑 关键：只搜横图 (适合桌面)
                          } #
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("photos", []):
                        resources.append({
                            "title": f"{item.get('alt', '无标题')[:50]} - {item['photographer']}",
                            "description": f"由 {item['photographer']} 拍摄的精美图片",
                            "category": "摄影",
                            "image_url": item['src']['large2x'],
                            "thumbnail_url": item['src']['medium'],
                            "download_link": item['src']['original'],
                            "source": "Pexels",
                            "author": item['photographer'],
                            "license_type": "Pexels License",
                            "original_url": item['url'],
                            "tags": [],
                            "is_active": True
                        })
                else: 
                    st.error(f"Pexels API 请求失败，状态码：{response.status_code}")       
                        
            elif source == "pixabay":
                # Pixabay API
                url = f"https://pixabay.com/api/"
                params = {
                    "key": st.secrets.get("external_api", {}).get("pixabay_key", "YOUR_PIXABAY_API_KEY"),
                    "q": query,
                    "image_type": "photo",
                    "per_page": min(limit, 30)
                }
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("hits", []):
                        resources.append({
                            "title": f"{item.get('tags', '无标题')} - {item['user']}",
                            "description": f"由 {item['user']} 上传的图片",
                            "category": "综合",
                            "image_url": item['largeImageURL'],
                            "thumbnail_url": item['previewURL'],
                            "download_link": item['imageURL'],
                            "source": "Pixabay",
                            "author": item['user'],
                            "license_type": "Pixabay License",
                            "original_url": item['pageURL'],
                            "tags": item.get('tags', '').split(',')[:5],
                            "is_active": True
                        })
            
            return {"ok": True, "data": resources, "count": len(resources)}
            
        except requests.exceptions.RequestException as e:
            st.error(f"网络请求失败：{str(e)}")
            return {"ok": False, "error": f"网络请求失败：{str(e)}"}
        except Exception as e:
            st.error(f"获取外部资源失败：{str(e)}")
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
        

    def temp_test(self,query, limit=20):
        
        """搜索素材
        (注意：Supabase Python 客户端的 or_ 语法可能需要构造字符串，如上所示 f"title.ilike.%{query}%,description.ilike.%{query}%" 是最稳妥的写法)
        """
        try:
            # 使用 or_ 组合条件：标题包含 OR 描述包含
            response = self.client.table("assets").select("*")\
                .eq("is_active", True)\
                .or_(f"title.ilike.%{query}%,description.ilike.%{query}%")\
                .limit(limit)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []    