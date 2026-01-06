"""
NLP理解模块
负责将自然语言转换为结构化的大数据处理任务
"""

from .query_analyzer import QueryAnalyzer
from .intent_recognizer import IntentRecognizer

__all__ = ['QueryAnalyzer', 'IntentRecognizer']
