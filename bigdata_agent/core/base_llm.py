"""
基础LLM抽象类
定义LLM接口规范
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseLLM(ABC):
    """基础LLM抽象类"""

    def __init__(self, api_key: str, model_name: Optional[str] = None):
        """初始化基础LLM"""
        self.api_key = api_key
        self.model_name = model_name or self._get_default_model()

    @abstractmethod
    def _get_default_model(self) -> str:
        """获取默认模型名称"""
        pass

    @abstractmethod
    def invoke(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """调用LLM生成回复"""
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        pass

    def validate_response(self, response: str) -> str:
        """验证和清理响应"""
        if response is None:
            return ""

        # 移除多余的空白字符
        response = response.strip()

        # 可以在这里添加更多的响应验证逻辑
        return response

    def estimate_tokens(self, text: str) -> int:
        """估算文本的token数量（简单实现）"""
        # 简单估算：英文约4字符=1token，中文约1.5字符=1token
        if not text:
            return 0

        # 粗略估算：平均每个字符约0.3个token
        return max(1, int(len(text) * 0.3))
