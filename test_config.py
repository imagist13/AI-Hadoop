#!/usr/bin/env python3
"""
测试配置文件加载和LLM初始化
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config_loading():
    """测试配置文件加载"""
    print("=== 测试配置文件加载 ===")

    try:
        from llms.settings_loader import load_settings_from_json, setup_environment_from_settings

        # 尝试加载配置
        settings = load_settings_from_json()
        print(f"✅ 成功加载配置: {len(settings)} 个配置项")

        # 显示配置项（不显示敏感信息）
        for key in settings.keys():
            if 'KEY' in key.upper() or 'SECRET' in key.upper():
                print(f"  - {key}: [已配置]")
            else:
                print(f"  - {key}: {settings[key]}")

        # 设置环境变量
        setup_environment_from_settings(settings)
        print("✅ 环境变量设置完成")

        return True
    except FileNotFoundError as e:
        print(f"❌ 配置文件未找到: {e}")
        return False
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def test_siliconflow_llm():
    """测试硅基流动LLM初始化"""
    print("\n=== 测试硅基流动LLM初始化 ===")

    try:
        from llms.siliconflow_llm import SiliconFlowLLM, get_chat_model

        # 测试LLM实例化
        llm = SiliconFlowLLM()
        print("✅ SiliconFlowLLM 实例化成功")

        # 测试模型信息获取
        model_info = llm.get_model_info()
        print(f"✅ 模型信息: {model_info}")

        # 测试ChatOpenAI实例化
        chat_model = get_chat_model()
        print("✅ ChatOpenAI 实例化成功"        print(f"   模型: {chat_model.model_name}")
        print(f"   温度: {chat_model.temperature}")

        return True
    except ValueError as e:
        if "API Key" in str(e):
            print("❌ API Key 未配置，请设置 SILICONFLOW_API_KEY 环境变量或在 setting.json 中配置")
        else:
            print(f"❌ LLM 初始化失败: {e}")
        return False
    except Exception as e:
        print(f"❌ LLM 初始化失败: {e}")
        return False

def test_api_connectivity():
    """测试API连接性"""
    print("\n=== 测试API连接性 ===")

    try:
        from llms.siliconflow_llm import SiliconFlowLLM

        llm = SiliconFlowLLM()
        # 尝试一个简单的API调用
        response = llm.invoke(
            system_prompt="你是一个测试助手，请简短回复。",
            user_prompt="请回复 '配置测试成功'",
            temperature=0.1,
            max_tokens=50
        )

        print(f"✅ API 调用成功: {response[:50]}...")
        return True
    except Exception as e:
        print(f"❌ API 调用失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始配置测试\n")

    # 测试配置加载
    config_ok = test_config_loading()

    if not config_ok:
        print("\n❌ 配置测试失败，请检查 setting.json 文件是否存在且格式正确")
        return

    # 测试LLM初始化
    llm_ok = test_siliconflow_llm()

    if not llm_ok:
        print("\n❌ LLM初始化失败，请检查API Key配置")
        return

    # 测试API连接（可选）
    print("\n是否测试API连接？(y/n): ", end="")
    test_api = input().lower().strip() == 'y'

    if test_api:
        api_ok = test_api_connectivity()
        if api_ok:
            print("\n🎉 所有测试通过！配置成功！")
        else:
            print("\n⚠️  LLM初始化成功，但API连接失败，请检查网络和API Key")
    else:
        print("\n🎉 配置测试通过！LLM初始化成功！")

if __name__ == "__main__":
    main()
