#!/usr/bin/env python3
"""
命令行接口
提供命令行方式使用BigData Agent
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from bigdata_agent import BigDataAgent


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="BigData Agent - 离线大数据处理智能代理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 基本查询
  python -m bigdata_agent.web.cli "统计昨天用户注册数"

  # 指定输出格式
  python -m bigdata_agent.web.cli "分析各省份销售额" --format chart

  # 保存结果到文件
  python -m bigdata_agent.web.cli "查询订单数据" --output result.json

  # 预览查询（不执行完整查询）
  python -m bigdata_agent.web.cli "统计用户数据" --preview

  # 估算查询成本
  python -m bigdata_agent.web.cli "复杂分析查询" --estimate-cost
        """
    )

    parser.add_argument('query', nargs='?', help='自然语言查询')
    parser.add_argument('-f', '--format', choices=['json', 'csv', 'chart', 'table'],
                       default='json', help='输出格式 (默认: json)')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-e', '--engine', choices=['spark', 'hive'],
                       default='spark', help='执行引擎 (默认: spark)')
    parser.add_argument('--preview', action='store_true',
                       help='预览查询结果（采样）')
    parser.add_argument('--estimate-cost', action='store_true',
                       help='估算查询成本')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='详细输出')

    args = parser.parse_args()

    if not args.query and not args.estimate_cost:
        parser.print_help()
        return

    try:
        # 初始化Agent
        print("🚀 启动BigData Agent...")
        agent = BigDataAgent(engine_type=args.engine)

        # 连接执行引擎
        print(f"🔌 连接到 {args.engine} 引擎...")
        if not agent.connect():
            print("❌ 无法连接到执行引擎")
            sys.exit(1)

        with agent:
            if args.estimate_cost:
                # 估算查询成本
                if not args.query:
                    print("❌ 估算成本需要提供查询语句")
                    sys.exit(1)

                print(f"📊 估算查询成本: {args.query}")
                result = agent.estimate_query_cost(args.query)

                if result['success']:
                    estimation = result['estimation']
                    print("\n📈 成本估算结果:"                    print(f"   预计执行时间: {estimation['estimated_minutes']:.1f} 分钟")
                    print(f"   复杂度因子: {estimation['complexity_factor']:.2f}")
                    print(f"   预估数据量: {estimation['estimated_row_count']} 行")
                else:
                    print(f"❌ 估算失败: {result['error']}")

            elif args.preview:
                # 预览查询
                print(f"👀 预览查询: {args.query}")
                result = agent.preview_query(args.query)

                if result['success']:
                    preview_data = result.get('preview_data', {})
                    if isinstance(preview_data, dict) and 'rows' in preview_data:
                        rows = preview_data['rows']
                        print(f"\n📋 预览数据 (前{len(rows)}行):")
                        if rows:
                            # 打印表头
                            headers = list(rows[0].keys())
                            print(" | ".join(f"{h:<15}" for h in headers))
                            print("-" * (len(headers) * 18))

                            # 打印数据
                            for row in rows[:5]:  # 只显示前5行
                                values = [str(row.get(h, ''))[:15] for h in headers]
                                print(" | ".join(f"{v:<15}" for v in values))
                    else:
                        print(f"预览数据: {preview_data}")
                else:
                    print(f"❌ 预览失败: {result['error']}")

            else:
                # 执行查询
                print(f"🔍 执行查询: {args.query}")
                result = agent.query(args.query, output_format=args.format)

                if result['success']:
                    print("✅ 查询执行成功!")

                    # 显示结果摘要
                    metadata = result.get('metadata', {})
                    print("
📊 结果摘要:"                    print(f"   数据行数: {metadata.get('row_count', 0)}")
                    print(f"   执行时间: {metadata.get('execution_time', 0):.2f}秒")
                    print(f"   输出格式: {args.format}")

                    # 保存结果到文件
                    if args.output:
                        from bigdata_agent.result.result_processor import ResultProcessor
                        processor = ResultProcessor()

                        success = processor.export_result(result, args.output, args.format)
                        if success:
                            print(f"💾 结果已保存到: {args.output}")
                        else:
                            print("❌ 保存结果失败")

                    # 显示详细结果（如果不是保存到文件）
                    elif args.verbose:
                        print(f"\n📄 详细结果:\n{json.dumps(result, ensure_ascii=False, indent=2)}")

                else:
                    print(f"❌ 查询执行失败: {result.get('error', '未知错误')}")
                    sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
