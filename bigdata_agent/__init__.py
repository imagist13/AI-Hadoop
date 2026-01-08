"""
离线大数据处理智能代理
"""

from .core.agent import BigDataAgent
from .core.base_llm import BaseLLM

# 导入外部llms模块
try:
    from llms import SiliconFlowLLM, get_chat_model
    _llms_available = True
except ImportError:
    _llms_available = False

__version__ = "0.1.0"
__author__ = "BigData Agent Team"

__all__ = ['BigDataAgent', 'BaseLLM']

if _llms_available:
    __all__.extend(['SiliconFlowLLM', 'get_chat_model'])
