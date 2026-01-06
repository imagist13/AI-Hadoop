"""
任务解析模块
将NLP分析结果转换为具体的SQL/HQL查询和处理逻辑
"""

from .sql_generator import SQLGenerator
from .task_builder import TaskBuilder

__all__ = ['SQLGenerator', 'TaskBuilder']
