#!/usr/bin/env python3
"""
BigData Agent集成测试
"""

import sys
import os
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_nlp_components():
    """测试NLP组件"""
    print("=== 测试NLP组件 ===")

    try:
        from bigdata_agent.nlp.intent_recognizer import IntentRecognizer
        from bigdata_agent.nlp.query_analyzer import QueryAnalyzer

        # 测试意图识别器
        recognizer = IntentRecognizer()

        test_queries = [
            "统计昨天用户注册数",
            "分析各省份销售额变化趋势",
            "筛选活跃用户",
            "按城市分组统计订单量"
        ]

        for query in test_queries:
            result = recognizer.recognize_intent(query)
            print(f"查询: {query}")
            print(f"  意图: {result.intent.value} (置信度: {result.confidence:.2f})")

        # 测试查询分析器
        analyzer = QueryAnalyzer()
        analyzed = analyzer.analyze_query("统计昨天用户注册数")

        print("\n查询分析结果:")
        print(f"  原始查询: {analyzed.original_query}")
        print(f"  意图: {analyzed.intent_result.intent.value}")
        print(f"  数据源: {analyzed.data_source.table}")
        print(f"  置信度: {analyzed.confidence_score:.2f}")

        return True

    except Exception as e:
        print(f"❌ NLP组件测试失败: {e}")
        return False

def test_task_builder():
    """测试任务构建器"""
    print("\n=== 测试任务构建器 ===")

    try:
        from bigdata_agent.nlp.query_analyzer import QueryAnalyzer
        from bigdata_agent.task.task_builder import TaskBuilder

        analyzer = QueryAnalyzer()
        builder = TaskBuilder()

        analyzed_query = analyzer.analyze_query("统计各省份用户数")
        task = builder.build_task(analyzed_query, engine_type="spark")

        print("任务构建结果:")
        print(f"  任务ID: {task.task_config.task_id}")
        print(f"  任务类型: {task.task_config.task_type}")
        print(f"  SQL: {task.sql_query[:100]}...")

        # 估算执行时间
        estimation = builder.estimate_execution_time(task)
        print(f"  预估时间: {estimation['estimated_minutes']:.1f}分钟")

        return True

    except Exception as e:
        print(f"❌ 任务构建器测试失败: {e}")
        return False

def test_result_processor():
    """测试结果处理器"""
    print("\n=== 测试结果处理器 ===")

    try:
        from bigdata_agent.result.result_processor import ResultProcessor
        from bigdata_agent.nlp.query_analyzer import QueryAnalyzer

        processor = ResultProcessor()
        analyzer = QueryAnalyzer()

        # 模拟执行结果
        mock_result = {
            'success': True,
            'data': [
                {'province': '北京', 'count': 1000},
                {'province': '上海', 'count': 800},
                {'province': '广州', 'count': 600}
            ],
            'columns': ['province', 'count'],
            'row_count': 3,
            'execution_time': 2.5,
            'task_id': 'test-task-001'
        }

        analyzed_query = analyzer.analyze_query("统计各省份用户数")

        # 测试不同格式的输出
        for fmt in ['json', 'table']:
            processed = processor.process_result(mock_result, analyzed_query, fmt)
            print(f"  {fmt.upper()}格式处理成功: {processed['success']}")

        return True

    except Exception as e:
        print(f"❌ 结果处理器测试失败: {e}")
        return False

def test_agent_initialization():
    """测试Agent初始化"""
    print("\n=== 测试Agent初始化 ===")

    try:
        from bigdata_agent import BigDataAgent

        # 测试Agent创建
        agent = BigDataAgent(engine_type="spark")
        print("✅ Agent创建成功")

        # 测试状态查询
        status = agent.get_status()
        print(f"✅ 状态查询成功: 连接状态 {status['connected']}")

        # 测试支持的引擎
        engines = agent.list_supported_engines()
        print(f"✅ 支持的引擎: {engines}")

        return True

    except Exception as e:
        print(f"❌ Agent初始化测试失败: {e}")
        return False

def test_query_analysis():
    """测试查询分析功能"""
    print("\n=== 测试查询分析功能 ===")

    try:
        from bigdata_agent.nlp.query_analyzer import QueryAnalyzer

        analyzer = QueryAnalyzer()

        test_cases = [
            "统计昨天的用户注册数",
            "分析各城市的销售额变化",
            "查找活跃用户列表",
            "按月份统计订单趋势",
            "筛选高价值客户"
        ]

        for query in test_cases:
            analyzed = analyzer.analyze_query(query)
            print(f"\n查询: {query}")
            print(f"  意图: {analyzed.intent_result.intent.value}")
            print(f"  置信度: {analyzed.confidence_score:.2f}")
            print(f"  数据源: {analyzed.data_source.table}")

        return True

    except Exception as e:
        print(f"❌ 查询分析测试失败: {e}")
        return False

def test_config_loading():
    """测试配置加载"""
    print("\n=== 测试配置加载 ===")

    try:
        from bigdata_agent.llms.settings_loader import load_settings_from_json

        # 尝试加载配置（如果setting.json存在）
        try:
            settings = load_settings_from_json()
            print("✅ 配置文件加载成功")
            print(f"  配置项数量: {len(settings)}")
        except FileNotFoundError:
            print("⚠️ 配置文件不存在，使用默认配置")
        except Exception as e:
            print(f"⚠️ 配置加载失败，使用默认配置: {e}")

        return True

    except Exception as e:
        print(f"❌ 配置加载测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始BigData Agent测试套件\n")

    tests = [
        ("配置加载", test_config_loading),
        ("NLP组件", test_nlp_components),
        ("任务构建器", test_task_builder),
        ("结果处理器", test_result_processor),
        ("Agent初始化", test_agent_initialization),
        ("查询分析", test_query_analysis)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - 通过")
            else:
                print(f"❌ {test_name} - 失败")
        except Exception as e:
            print(f"❌ {test_name} - 异常: {e}")

    print(f"\n📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！BigData Agent准备就绪！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关组件")
        return False

def main():
    """主函数"""
    success = run_all_tests()

    # 如果有配置文件，测试完整功能
    if Path("setting.json").exists():
        print("\n🔧 检测到配置文件，测试完整Agent功能...")

        try:
            from bigdata_agent import BigDataAgent

            agent = BigDataAgent()
            if agent.connect():
                print("✅ Agent连接成功")

                # 测试简单查询
                result = agent.estimate_query_cost("统计用户数据")
                if result['success']:
                    print("✅ 成本估算功能正常")
                else:
                    print(f"⚠️ 成本估算功能异常: {result.get('error')}")

                agent.disconnect()
            else:
                print("⚠️ Agent连接失败（可能是缺少依赖或配置）")

        except Exception as e:
            print(f"⚠️ 完整功能测试异常: {e}")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
