"""
结果格式化器
提供多种数据输出格式
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json

from ..nlp.query_analyzer import AnalyzedQuery


class ResultFormatter(ABC):
    """结果格式化器抽象基类"""

    @abstractmethod
    def format(self, data: List[Dict], columns: List[str],
              analyzed_query: AnalyzedQuery, **kwargs) -> Any:
        """格式化数据"""
        pass


class JSONFormatter(ResultFormatter):
    """JSON格式化器"""

    def format(self, data: List[Dict], columns: List[str],
              analyzed_query: AnalyzedQuery, **kwargs) -> Dict[str, Any]:
        """格式化为JSON结构"""
        return {
            'columns': columns,
            'rows': data,
            'summary': {
                'total_rows': len(data),
                'query_type': analyzed_query.intent_result.intent.value,
                'confidence': analyzed_query.confidence_score
            }
        }


class CSVFormatter(ResultFormatter):
    """CSV格式化器"""

    def format(self, data: List[Dict], columns: List[str],
              analyzed_query: AnalyzedQuery, **kwargs) -> str:
        """格式化为CSV字符串"""
        if not data:
            return ""

        import io
        output = io.StringIO()

        # 如果没有指定列，使用数据中的键
        if not columns:
            columns = list(data[0].keys()) if data else []

        # 写入CSV
        import csv
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(data)

        return output.getvalue()


class TableFormatter(ResultFormatter):
    """表格格式化器"""

    def format(self, data: List[Dict], columns: List[str],
              analyzed_query: AnalyzedQuery, **kwargs) -> Dict[str, Any]:
        """格式化为表格结构"""
        if not columns and data:
            columns = list(data[0].keys())

        # 计算列宽
        column_widths = {}
        for col in columns:
            max_width = len(col)
            for row in data:
                value_str = str(row.get(col, ''))
                max_width = max(max_width, len(value_str))
            column_widths[col] = min(max_width, 50)  # 最大宽度限制

        return {
            'type': 'table',
            'columns': columns,
            'rows': data,
            'column_widths': column_widths,
            'total_rows': len(data)
        }


class ChartFormatter(ResultFormatter):
    """图表格式化器"""

    def format(self, data: List[Dict], columns: List[str],
              analyzed_query: AnalyzedQuery, **kwargs) -> Dict[str, Any]:
        """格式化为图表配置"""
        if not data:
            return {'type': 'chart', 'data': [], 'error': '无数据'}

        intent = analyzed_query.intent_result.intent.value

        # 根据意图确定图表类型和配置
        if intent == 'statistics':
            chart_config = self._create_bar_chart(data, columns)
        elif intent == 'trend':
            chart_config = self._create_line_chart(data, columns)
        elif intent == 'distribution':
            chart_config = self._create_pie_chart(data, columns)
        elif intent == 'ranking':
            chart_config = self._create_bar_chart(data, columns, horizontal=True)
        else:
            chart_config = self._create_table_chart(data, columns)

        return chart_config

    def _create_bar_chart(self, data: List[Dict], columns: List[str],
                         horizontal: bool = False) -> Dict[str, Any]:
        """创建柱状图配置"""
        if len(columns) < 2:
            return self._create_table_chart(data, columns)

        # 假设第一列是标签，其他列是数值
        labels = [row[columns[0]] for row in data]
        datasets = []

        for i, col in enumerate(columns[1:], 1):
            values = [row.get(col, 0) for row in data]
            datasets.append({
                'label': col,
                'data': values,
                'backgroundColor': f'rgba({54 + i*30}, {162 - i*20}, {235 - i*10}, 0.6)',
                'borderColor': f'rgba({54 + i*30}, {162 - i*20}, {235 - i*10}, 1)',
                'borderWidth': 1
            })

        return {
            'type': 'bar',
            'horizontal': horizontal,
            'data': {
                'labels': labels,
                'datasets': datasets
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'legend': {'position': 'top'},
                    'title': {'display': True, 'text': '统计图表'}
                }
            }
        }

    def _create_line_chart(self, data: List[Dict], columns: List[str]) -> Dict[str, Any]:
        """创建线图配置"""
        if len(columns) < 2:
            return self._create_table_chart(data, columns)

        # 假设第一列是时间/X轴
        labels = [str(row[columns[0]]) for row in data]
        datasets = []

        for i, col in enumerate(columns[1:], 1):
            values = [row.get(col, 0) for row in data]
            datasets.append({
                'label': col,
                'data': values,
                'borderColor': f'rgba({75 + i*20}, {192 - i*15}, {192 - i*10}, 1)',
                'backgroundColor': f'rgba({75 + i*20}, {192 - i*15}, {192 - i*10}, 0.2)',
                'tension': 0.1
            })

        return {
            'type': 'line',
            'data': {
                'labels': labels,
                'datasets': datasets
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'legend': {'position': 'top'},
                    'title': {'display': True, 'text': '趋势图表'}
                }
            }
        }

    def _create_pie_chart(self, data: List[Dict], columns: List[str]) -> Dict[str, Any]:
        """创建饼图配置"""
        if len(columns) < 2 or len(data) > 20:  # 饼图不适合太多数据
            return self._create_table_chart(data, columns)

        # 使用前两个列：标签和数值
        labels = [str(row[columns[0]]) for row in data]
        values = [row.get(columns[1], 0) for row in data]

        # 生成颜色
        colors = []
        for i in range(len(data)):
            hue = (i * 137.5) % 360  # 黄金角度分割
            colors.append(f'hsl({hue}, 70%, 50%)')

        return {
            'type': 'pie',
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': values,
                    'backgroundColor': colors,
                    'borderColor': colors,
                    'borderWidth': 1
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'legend': {'position': 'right'},
                    'title': {'display': True, 'text': '分布图表'}
                }
            }
        }

    def _create_table_chart(self, data: List[Dict], columns: List[str]) -> Dict[str, Any]:
        """创建表格图表（降级方案）"""
        return {
            'type': 'table',
            'data': data,
            'columns': columns,
            'message': '数据已转换为表格格式'
        }
