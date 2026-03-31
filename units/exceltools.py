import streamlit as st
import pandas as pd
from   abc  import ABC, abstractmethod
from   io   import BytesIO

# ---合并策略： 抽象类
class MergeStrategy(ABC):
    @abstractmethod
    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame, **kwargs)->pd.DataFrame:
        pass

# --- 具体策略：按共同列左连接合并（类似 VLOOKUP）---
class LeftJoinStrategy(MergeStrategy):
    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame, on_col: str, **kwargs)->pd.DataFrame:
        return pd.merge(df1, df2, on= on_col ,how='left')
    
# --- 具体策略：上下拼接（行追加）---
class ConcatenateMerge(MergeStrategy):
    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame, **kwargs)->pd.DataFrame:
        return pd.concat([df1, df2], ignore_index=True)


# --- 核心 Excel 合并工具类 ---
class ExcelMerger:
    def __init__(self, merge_strategy: MergeStrategy=None):
        self.strategy = merge_strategy

    def set_strategy(self, merge_strategy: MergeStrategy):
        """动态切换合并策略"""
        self.strategy = merge_strategy

    def read_file(self, file_path: str)->pd.DataFrame:
        """支持 xlsx、xls、csv 文件读取"""
        if file_path.name.endswith('.xlsx') or file_path.name.endswith('.xls'):
            return pd.read_excel(file_path)
        elif file_path.name.endswith('.csv'):
            return pd.read_csv(file_path)
        else:
            raise ValueError("不支持的文件格式")
    def execute_merge(self, file1, file2, **kwargs) -> pd.DataFrame:
        """执行合并流程"""
        df1 = self.read_file(file1)
        df2 = self.read_file(file2)
        return self.strategy.merge(df1, df2, **kwargs)
    # def execute_merge(self, file_paths: list, **kwargs)->pd.DataFrame:
    #     """合并多个 Excel 文件"""
    #     dfs = [self.read_file(file_path) for file_path in file_paths]
    #     return self.strategy.merge(*dfs, **kwargs)   

    def to_excel_bytes(self, df: pd.DataFrame)->bytes: 
        """将 DataFrame 转换为 Excel 文件并返回字节流"""
        output = BytesIO()
        with pd.ExcelWriter(output) as writer:  #, engine='xlsxwriter'
            df.to_excel(writer, index=False, sheet_name='合并结果')
        return output.getvalue()    



    

