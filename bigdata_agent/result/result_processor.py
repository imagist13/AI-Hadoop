"""
结果处理器
处理执行结果并格式化输出
"""

import json
import csv
import io
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ..nlp.query_analyzer import AnalyzedQuery


class ResultProcessor:
    """结果处理器"""

    def __init__(self):
        """初始化结果处理器"""
        self.formatters = {
            'json': JSONFormatter(),
            'csv': CSVFormatter(),
            'chart': ChartFormatter(),
            'table': TableFormatter()
        }

    def process_result(self, execution_result: Dict[str, Any],
                      analyzed_query: AnalyzedQuery,
                      output_format: str = 'json',
                      **kwargs) -> Dict[str, Any]:
        """
        处理执行结果

        Args:
            execution_result: 执行引擎返回的结果
            analyzed_query: 解析后的查询结构
            output_format: 输出格式 (json, csv, chart, table)
            **kwargs: 额外参数

        Returns:
            dict: 处理后的结果
        """
        if not execution_result.get('success', False):
            # 执行失败，返回错误信息
            return {
                'success': False,
                'error': execution_result.get('error', '未知错误'),
                'task_id': execution_result.get('task_id'),
                'execution_time': execution_result.get('execution_time', 0),
                'timestamp': datetime.now().isoformat()
            }

        # 获取对应的格式化器
        formatter = self.formatters.get(output_format)
        if not formatter:
            formatter = self.formatters['json']

        # 处理数据
        processed_data = formatter.format(
            data=execution_result.get('data', []),
            columns=execution_result.get('columns', []),
            analyzed_query=analyzed_query,
            **kwargs
        )

        # 添加元信息
        result = {
            'success': True,
            'data': processed_data,
            'metadata': {
                'task_id': execution_result.get('task_id'),
                'row_count': execution_result.get('row_count', 0),
                'execution_time': execution_result.get('execution_time', 0),
                'output_format': output_format,
                'timestamp': datetime.now().isoformat(),
                'query_summary': self._generate_query_summary(analyzed_query)
            }
        }

        return result

    def _generate_query_summary(self, analyzed_query: AnalyzedQuery) -> Dict[str, Any]:
        """生成查询摘要"""
        return {
            'original_query': analyzed_query.original_query,
            'intent': analyzed_query.intent_result.intent.value,
            'data_source': analyzed_query.data_source.table,
            'has_conditions': len(analyzed_query.conditions) > 0,
            'has_aggregations': analyzed_query.aggregations is not None,
            'confidence_score': analyzed_query.confidence_score
        }

    def export_result(self, processed_result: Dict[str, Any],
                     file_path: str,
                     format_type: Optional[str] = None) -> bool:
        """
        导出结果到文件

        Args:
            processed_result: 处理后的结果
            file_path: 输出文件路径
            format_type: 导出格式，如果不指定则根据文件扩展名判断

        Returns:
            bool: 导出是否成功
        """
        if not processed_result.get('success', False):
            print("结果处理失败，无法导出")
            return False

        # 根据文件扩展名确定格式
        if not format_type:
            if file_path.endswith('.json'):
                format_type = 'json'
            elif file_path.endswith('.csv'):
                format_type = 'csv'
            else:
                format_type = 'json'

        try:
            formatter = self.formatters.get(format_type, self.formatters['json'])

            # 获取原始数据
            data = processed_result.get('data', {})

            # 导出数据
            with open(file_path, 'w', encoding='utf-8') as f:
                if format_type == 'json':
                    json.dump(data, f, ensure_ascii=False, indent=2)
                elif format_type == 'csv':
                    # CSV格式需要特殊处理
                    if isinstance(data, dict) and 'rows' in data:
                        writer = csv.DictWriter(f, fieldnames=data.get('columns', []))
                        writer.writeheader()
                        writer.writerows(data['rows'])
                    elif isinstance(data, list) and data:
                        if isinstance(data[0], dict):
                            writer = csv.DictWriter(f, fieldnames=data[0].keys())
                            writer.writeheader()
                            writer.writerows(data)

            print(f"✅ 结果已导出到: {file_path}")
            return True

        except Exception as e:
            print(f"❌ 导出失败: {e}")
            return False

    def generate_chart_config(self, processed_result: Dict[str, Any],
                            analyzed_query: AnalyzedQuery) -> Dict[str, Any]:
        """
        生成图表配置（用于前端展示）

        Returns:
            dict: 图表配置
        """
        if not processed_result.get('success', False):
            return {'error': '无有效数据生成图表'}

        data = processed_result.get('data', {})
        intent = analyzed_query.intent_result.intent.value

        # 根据查询意图选择图表类型
        chart_type = self._determine_chart_type(intent, data)

        config = {
            'type': chart_type,
            'data': data,
            'title': f"{analyzed_query.intent_result.intent.value}结果",
            'query': analyzed_query.original_query,
            'timestamp': processed_result.get('metadata', {}).get('timestamp')
        }

        return config

    def _determine_chart_type(self, intent: str, data: Any) -> str:
        """根据查询意图确定图表类型"""
        chart_mapping = {
            'statistics': 'bar',
            'trend': 'line',
            'comparison': 'bar',
            'distribution': 'pie',
            'ranking': 'bar',
            'correlation': 'scatter'
        }

        return chart_mapping.get(intent, 'table')

    def paginate_result(self, processed_result: Dict[str, Any],
                       page: int = 1,
                       page_size: int = 100) -> Dict[str, Any]:
        """
        对结果进行分页

        Args:
            processed_result: 处理后的结果
            page: 页码（从1开始）
            page_size: 每页大小

        Returns:
            dict: 分页后的结果
        """
        if not processed_result.get('success', False):
            return processed_result

        data = processed_result.get('data', {})

        # 处理不同数据格式
        if isinstance(data, dict) and 'rows' in data:
            rows = data['rows']
            total_count = len(rows)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size

            paginated_data = {
                'columns': data.get('columns', []),
                'rows': rows[start_idx:end_idx],
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': (total_count + page_size - 1) // page_size,
                    'has_next': end_idx < total_count,
                    'has_prev': page > 1
                }
            }
        elif isinstance(data, list):
            total_count = len(data)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size

            paginated_data = {
                'rows': data[start_idx:end_idx],
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': (total_count + page_size - 1) // page_size,
                    'has_next': end_idx < total_count,
                    'has_prev': page > 1
                }
            }
        else:
            # 其他格式不分页
            paginated_data = data

        result = processed_result.copy()
        result['data'] = paginated_data

        return result
