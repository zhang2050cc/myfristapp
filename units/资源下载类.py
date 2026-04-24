

import streamlit as st
import requests
from session_state import AppState


# 素材下载 Pexels Unsplash Pixabay 
class MaterialDownLoad():
    def __init__(self, auth_state = None):
        #self.search_source = ["pexels", "unsplash", "pixabay"]
        self.auth_state = auth_state
        AppState.init_session_state()

        #self.search_source = "" #["pexels", "unsplash", "pixabay"]
       
    @property
    def search_result(self):
        return st.session_state["external_search_results"] 
    @search_result.setter
    def search_result(self,value):
        st.session_state["external_search_results"] = value
    
    @property
    def image_data(self):
        return st.session_state["image_data"]    
    @image_data.setter
    def image_data(self,value):
        st.session_state["image_data"] = value





    def extract_image_urls(self, photo, size_option, source):
        """从不同API来源的单张图片数据中提取URL信息"""
        
        # 定义基础URL字典结构
        url_info = {
            "image_url": None,          # 页面展示用
            "download_url": None,       # 下载用
            "original_image_url": None, # 原图链接
            "photographer": None        # 摄影师信息
        }

        # 根据API来源进行字段映射
        match source:
            case "pexels":
                # 处理Pexels API结构
                src = photo.get("src", {})
                url_info.update({
                    "image_url": src.get(size_option, src.get("medium", "")),
                    "download_url": src.get("original", src.get("large2x", src.get("large", ""))),
                    "original_image_url": photo.get("url", "#"),
                    "photographer": photo.get("photographer", "Unknown")
                })
            
            case "unsplash":
                # 处理Unsplash API结构
                urls = photo.get("urls", {})
                url_info.update({
                    "image_url": urls.get(size_option, urls.get("regular", "")),    #regular以jpg格式返回宽度为1080像素的照片
                    "download_url": urls.get("full", urls.get("regular", "")),          #full 以最大尺寸以jpg格式返回照片
                    "original_image_url": photo.get("links", {}).get("html", "#"),
                    "photographer": photo.get("user", {}).get("name", "Unknown")
                })
            
            case "pixabay":
                # 处理Pixabay API结构
                url_info.update({
                    "image_url": photo.get(size_option, photo.get("webformatURL", "")),
                    "download_url": photo.get("largeImageURL", photo.get("imageURL", "")),
                    "original_image_url": photo.get("pageURL", "#"),
                    "photographer": photo.get("user", "Unknown")
                })
        return url_info


    

    def GetUrlBySearchResults(self,data,source):

        # 定义固定键的字典
        photo_info = {
            "page": 1,          # 默认页码
            "per_page": 15,     # 默认每页数量
            "photos": [],       # 默认空列表存储图片数据
            "total_results": 0, # 默认总结果数为0
            "next_page": None,  # 默认无下一页
            "prev_page": None , # 默认无上一页
        }

       # data = self.search_result
        # if data is None:
        #     return photo_info

        match source:
            case "pexels":
                 # 快速赋值方法：使用字典推导式
                photo_info.update({
                    k: data.get(k) for k in photo_info.keys()
                })

            case "unsplash":
                # Unsplash可能需要字段转换
                # data ={
                #         "total":0,
                #         "total_pages":0,
                #         "results":[]
                #         }
                
                photo_info.update({
                    "page": data.get("page"),
                    "per_page": data.get("per_page"),
                    "photos": data.get("results", []),  # Unsplash使用results字段
                    "total_results": data.get("total", 0),
                    "next_page": data.get("next_page"),
                    "prev_page": data.get("prev_page")
                })

            case "pixabay":

                # Pixabay可能需要不同的字段映射
                photo_info.update({
                    "page": data.get("page"),
                    "per_page": data.get("per_page"),
                    "photos": data.get("hits", []),
                    "total_results": data.get("total", 0),
                    "next_page": data.get("next_page"),
                    "prev_page": data.get("prev_page")
                })
                pass

            case _:
                pass

        return photo_info    




    def ImageDwon(self,img_url):
        with st.spinner(f"🔄 正在下载中..."):
            try:
                #img_data = requests.get(img_url).content
                response = requests.get(img_url)
                if response.status_code == 200:
                    self.image_data = response.content
                    self.auth_state.status = "search_success"
                    return self.image_data
            except Exception as e:
                st.error(f"下载出错了...{str(e)}")    
            


    #搜索的网址固定在代码中。api_key需要用户自己提供(用一个文本框接收)
    def search_material(self,query: str,source: str, apikey: str, limit: int = 15,current_page: int=1, direction: str=""):
        
        self.auth_state.status = "searching"
        self.auth_state.message = f"正在使用 {source} 搜索 '{query}' 素材，最多返回 {limit} 条结果。"
        
        #Access_Key      = "Zg8saXriaSwNS-BL2C0IZi5hskMii5YytR9VBo5iHqs"   #访问密钥
        #图片方向，orientation 可选值：landscape (横向), portrait (纵向), square (方形)
        match source:
            case "pexels":
                url     = "https://api.pexels.com/v1/search"
                headers = {"Authorization": apikey}
                params  = {"query": query, "page": current_page, "per_page": min(limit,30), "orientation":direction}
            case "unsplash":
                
                url     = "https://api.unsplash.com/search/photos"
                headers = {"Authorization": f"Client-ID {apikey}","Accept": "application/json" }# 明确指定接收 JSON
                params  = {"query": query, "page": current_page, "per_page": min(limit,30), "orientation":direction}#
            case "pixabay":
                url     = "https://pixabay.com/api/" #https://pixabay.com/api/
                headers = None
                params  = {"key": apikey, "q": query, "page": current_page, "per_page": min(limit,30), "orientation":direction}
                #response = requests.get(url, params=params)
                #return response.json()
            case _:
                st.info("暂不支持此功能")    
                


        with st.spinner(f"🔄 正在搜索第 {current_page} 页... |  图片方向： {direction}"):
            # st.toast("正在搜索素材，请稍候...")
            # st.info(f"正在使用 {source} 搜索 '{query}' 素材，最多返回 {limit} 条结果。")
            # st.info(f"apikey: {apikey}")
            # st.info(f"我经过了这里{source}")
            # return
            try:
                response = requests.get(url, headers=headers, params=params)
                #return response.json()
                # st.toast(f"成功找到: {response.status_code}")
                # st.info(f"原始返回内容: {response.text}") # 👈 这一行最关键 "results"
                if response.status_code==200:
                    self.search_result = response.json()
                    #st.write(response.json())data.get("hits", []),

                    num_results = len(self.search_result.get("photos",
                                    self.search_result.get("results",self.search_result.get("hits", []))))
                    self.auth_state.status = "success"
                    self.auth_state.message = f"成功找到 {num_results} 条素材！"
                    
                else:
                    self.auth_state.status = "search_failed"
                    self.auth_state.message = f"搜索失败: {response.status_code}"
                    st.toast(f"搜索失败: {response.status_code}")
            except Exception as e:
                self.auth_state.status = "error"
                self.auth_state.message = f"搜索过程中发生错误: {str(e)}"
                st.toast(f"搜索失败，状态码: {str(e)}")
        
    
    










        