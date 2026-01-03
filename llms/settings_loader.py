"""
配置加载模块
从 setting.json 文件加载配置并设置环境变量
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


def _find_settings_file() -> Path:
    """查找 setting.json 文件"""
    paths = [
        Path("setting.json"),
        Path(__file__).parent.parent / "setting.json",
        Path.cwd() / "setting.json"
    ]
    for path in paths:
        if path.exists():
            return path
    raise FileNotFoundError("未找到 setting.json 文件")


def load_settings_from_json(json_path: Optional[str] = None) -> Dict[str, Any]:
    """从 JSON 文件加载配置"""
    if json_path is None:
        json_path = _find_settings_file()

    path = Path(json_path)
    with open(path, 'r', encoding='utf-8') as f:
        raw = json.load(f)

    if not isinstance(raw, dict):
        return raw

    # 合并配置
    settings = raw.get("settings", {}).copy()
    for k, v in raw.items():
        if k != "settings" and not isinstance(v, dict):
            settings[k] = v
    if "WAN_API_SETTINGS" in raw:
        settings["WAN_API_SETTINGS"] = raw["WAN_API_SETTINGS"]

    return settings


def setup_environment_from_settings(settings: Optional[Dict[str, Any]] = None) -> None:
    """从配置字典设置环境变量"""
    if settings is None:
        settings = load_settings_from_json()

    # 设置硅基流动环境变量
    env_mapping = {
        "SILICONFLOW_API_KEY": "SILICONFLOW_API_KEY",
        "SILICONFLOW_BASE_URL": "SILICONFLOW_BASE_URL",
        "SILICONFLOW_CHAT_MODEL": "SILICONFLOW_MODEL",
    }

    for json_key, env_key in env_mapping.items():
        if settings.get(json_key):
            os.environ[env_key] = str(settings[json_key])

    # 设置WAN API环境变量
    wan_settings = settings.get("WAN_API_SETTINGS", {})
    if wan_settings.get("WAN_API_URL"):
        os.environ["WAN_API_URL"] = str(wan_settings["WAN_API_URL"])
    if wan_settings.get("WAN_API_KEY"):
        os.environ["WAN_API_KEY"] = str(wan_settings["WAN_API_KEY"])


def load_and_setup_settings(json_path: Optional[str] = None) -> Dict[str, Any]:
    """加载配置并设置环境变量（便捷函数）"""
    settings = load_settings_from_json(json_path)
    setup_environment_from_settings(settings)
    return settings

