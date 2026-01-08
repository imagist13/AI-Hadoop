"""
硅基流动LLM实现
使用硅基流动API进行文本生成
"""

import os
from typing import Optional, Dict, Any
from openai import OpenAI
from langchain_openai import ChatOpenAI
from bigdata_agent.core.base_llm import BaseLLM


class SiliconFlowLLM(BaseLLM):
    """硅基流动LLM实现类"""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """初始化硅基流动客户端"""
        super().__init__(self._get_api_key(api_key), model_name)

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self._get_base_url()
        )
        self.default_model = model_name or self._get_model_name()

    def _get_default_model(self) -> str:
        """获取默认模型名称"""
        return self._get_model_name()

    def _get_from_settings(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """从配置文件获取设置"""
        try:
            from config.settings_loader import load_settings_from_json
            settings = load_settings_from_json()
            return settings.get(key, default)
        except:
            return default

    def _get_api_key(self, api_key: Optional[str] = None) -> str:
        """获取API密钥"""
        if api_key:
            return api_key

        api_key = os.getenv("SILICONFLOW_API_KEY") or self._get_from_settings("SILICONFLOW_API_KEY")
        if not api_key:
            raise ValueError("硅基流动API Key未找到！请设置SILICONFLOW_API_KEY环境变量或在setting.json中配置")
        return api_key

    def _get_base_url(self) -> str:
        """获取基础URL"""
        return os.getenv("SILICONFLOW_BASE_URL") or self._get_from_settings("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")

    def _get_model_name(self) -> str:
        """获取模型名称"""
        return os.getenv("SILICONFLOW_MODEL") or self._get_from_settings("SILICONFLOW_CHAT_MODEL", "deepseek-ai/DeepSeek-V3")
    
    def invoke(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """调用硅基流动API生成回复"""
        try:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 4000),
                stream=False
            )
            content = response.choices[0].message.content or "" if response.choices else ""
            return self.validate_response(content)
        except Exception as e:
            print(f"硅基流动API调用错误: {str(e)}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """获取当前模型信息"""
        return {
            "provider": "SiliconFlow",
            "model": self.default_model,
            "api_base": "https://api.siliconflow.cn/v1"
        }


def _get_config() -> tuple[str, str, str]:
    """获取硅基流动配置 (api_key, base_url, model_name)"""
    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        try:
            from config.settings_loader import load_settings_from_json
            settings = load_settings_from_json()
            api_key = settings.get("SILICONFLOW_API_KEY")
        except:
            pass
    if not api_key:
        raise ValueError("硅基流动API Key未找到！请设置SILICONFLOW_API_KEY环境变量或在setting.json中配置")

    base_url = os.getenv("SILICONFLOW_BASE_URL") or _get_from_settings_static("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
    model_name = os.getenv("SILICONFLOW_MODEL") or _get_from_settings_static("SILICONFLOW_CHAT_MODEL", "deepseek-ai/DeepSeek-V3")

    return api_key, base_url, model_name

def _get_from_settings_static(key: str, default: Optional[str] = None) -> Optional[str]:
    """静态方法：从配置文件获取设置"""
    try:
        from config.settings_loader import load_settings_from_json
        settings = load_settings_from_json()
        return settings.get(key, default)
    except:
        return default

def get_chat_model() -> ChatOpenAI:
    """获取LangChain兼容的聊天模型"""
    api_key, base_url, model_name = _get_config()
    return ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model_name,
        temperature=0.7,
        max_tokens=4000
    )

