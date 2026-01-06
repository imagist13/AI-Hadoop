"""
查询分析器
使用LLM将自然语言转换为结构化的数据处理任务
"""

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

from ..llms.siliconflow_llm import SiliconFlowLLM
from .intent_recognizer import IntentRecognizer, IntentResult


@dataclass
class DataSource:
    """数据源配置"""
    name: str
    type: str  # hive, spark, clickhouse, file, etc.
    table: str
    database: Optional[str] = None
    path: Optional[str] = None


@dataclass
class QueryCondition:
    """查询条件"""
    field: str
    operator: str  # =, >, <, >=, <=, like, in, between
    value: Any
    logical_op: str = "AND"  # AND, OR


@dataclass
class AggregationConfig:
    """聚合配置"""
    group_by: List[str]
    aggregations: Dict[str, str]  # field -> function (count, sum, avg, max, min)


@dataclass
class TimeRange:
    """时间范围"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    relative_days: Optional[int] = None  # 相对天数，如 -7 表示最近7天


@dataclass
class OutputConfig:
    """输出配置"""
    format: str = "json"  # json, csv, chart, table
    limit: Optional[int] = None
    sort_by: Optional[str] = None
    sort_order: str = "desc"  # asc, desc


@dataclass
class AnalyzedQuery:
    """解析后的查询结构"""
    original_query: str
    intent_result: IntentResult
    data_source: DataSource
    conditions: List[QueryCondition]
    aggregations: Optional[AggregationConfig] = None
    time_range: Optional[TimeRange] = None
    output_config: OutputConfig = OutputConfig()
    description: str = ""
    confidence_score: float = 0.0


class QueryAnalyzer:
    """查询分析器"""

    def __init__(self):
        """初始化查询分析器"""
        self.intent_recognizer = IntentRecognizer()
        self.llm = SiliconFlowLLM()

        # 预定义的数据源映射（可以从配置文件加载）
        self.data_source_mapping = {
            '用户': DataSource(name='users', type='hive', table='user_info', database='default'),
            '订单': DataSource(name='orders', type='hive', table='order_info', database='default'),
            '商品': DataSource(name='products', type='hive', table='product_info', database='default'),
            '日志': DataSource(name='logs', type='hive', table='user_logs', database='default'),
        }

    def analyze_query(self, query: str) -> AnalyzedQuery:
        """
        分析用户查询

        Args:
            query: 用户的自然语言查询

        Returns:
            AnalyzedQuery: 解析后的结构化查询
        """
        # 首先进行意图识别
        intent_result = self.intent_recognizer.recognize_intent(query)

        # 使用LLM进行深度分析
        llm_analysis = self._llm_deep_analysis(query, intent_result)

        # 解析数据源
        data_source = self._parse_data_source(query, llm_analysis)

        # 解析查询条件
        conditions = self._parse_conditions(query, llm_analysis)

        # 解析聚合配置
        aggregations = self._parse_aggregations(query, llm_analysis)

        # 解析时间范围
        time_range = self._parse_time_range(query, llm_analysis)

        # 解析输出配置
        output_config = self._parse_output_config(query, llm_analysis)

        # 计算置信度
        confidence_score = self._calculate_confidence(intent_result, llm_analysis)

        return AnalyzedQuery(
            original_query=query,
            intent_result=intent_result,
            data_source=data_source,
            conditions=conditions,
            aggregations=aggregations,
            time_range=time_range,
            output_config=output_config,
            description=llm_analysis.get('description', ''),
            confidence_score=confidence_score
        )

    def _llm_deep_analysis(self, query: str, intent_result: IntentResult) -> Dict[str, Any]:
        """使用LLM进行深度查询分析"""
        system_prompt = """
你是一个大数据查询分析专家。请分析用户的自然语言查询，将其转换为结构化的数据处理任务。

请以JSON格式返回以下信息：
{
  "data_entity": "识别的主要数据实体（用户、订单、商品等）",
  "query_type": "查询类型（统计、分析、筛选、聚合等）",
  "conditions": "查询条件描述",
  "aggregations": "聚合操作描述",
  "time_range": "时间范围描述",
  "output_requirements": "输出要求描述",
  "description": "简要描述这个查询的意图"
}

请确保返回有效的JSON格式。
"""

        user_prompt = f"""
用户查询：{query}
识别的意图：{intent_result.intent.value} (置信度: {intent_result.confidence:.2f})

请分析这个查询并返回结构化信息。
"""

        try:
            response = self.llm.invoke(system_prompt, user_prompt)
            # 尝试解析JSON响应
            return json.loads(response.strip())
        except (json.JSONDecodeError, Exception):
            # 如果LLM返回的不是有效JSON，返回默认分析
            return {
                "data_entity": intent_result.parameters.get('entity', 'unknown'),
                "query_type": intent_result.intent.value,
                "conditions": "无特定条件",
                "aggregations": "无聚合操作",
                "time_range": intent_result.parameters.get('time_range'),
                "output_requirements": "默认输出",
                "description": f"{intent_result.intent.value}查询"
            }

    def _parse_data_source(self, query: str, llm_analysis: Dict[str, Any]) -> DataSource:
        """解析数据源"""
        entity = llm_analysis.get('data_entity', '')

        # 从预定义映射中查找
        for key, data_source in self.data_source_mapping.items():
            if key in entity or key in query:
                return data_source

        # 默认返回用户数据源
        return self.data_source_mapping.get('用户', DataSource(
            name='default', type='hive', table='default_table', database='default'
        ))

    def _parse_conditions(self, query: str, llm_analysis: Dict[str, Any]) -> List[QueryCondition]:
        """解析查询条件"""
        conditions = []
        conditions_desc = llm_analysis.get('conditions', '')

        # 简单的时间条件解析
        if '昨天' in query:
            conditions.append(QueryCondition(
                field='date',
                operator='=',
                value=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            ))
        elif '今天' in query:
            conditions.append(QueryCondition(
                field='date',
                operator='=',
                value=datetime.now().strftime('%Y-%m-%d')
            ))
        elif '最近7天' in query or '过去一周' in query:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            conditions.append(QueryCondition(
                field='date',
                operator='>=',
                value=start_date
            ))

        return conditions

    def _parse_aggregations(self, query: str, llm_analysis: Dict[str, Any]) -> Optional[AggregationConfig]:
        """解析聚合配置"""
        aggregations_desc = llm_analysis.get('aggregations', '')

        if '分组' in query or '按' in query or 'group by' in query.lower():
            # 简单的聚合解析
            group_by = []
            aggregations = {}

            # 识别分组字段
            if '省份' in query:
                group_by.append('province')
            elif '城市' in query:
                group_by.append('city')
            elif '日期' in query or '时间' in query:
                group_by.append('date')

            # 识别聚合函数
            if '统计' in query or '计数' in query:
                aggregations['count'] = 'count(*)'
            elif '求和' in query or '总计' in query:
                aggregations['total'] = 'sum(amount)'

            if group_by or aggregations:
                return AggregationConfig(
                    group_by=group_by,
                    aggregations=aggregations
                )

        return None

    def _parse_time_range(self, query: str, llm_analysis: Dict[str, Any]) -> Optional[TimeRange]:
        """解析时间范围"""
        time_desc = llm_analysis.get('time_range') or llm_analysis.get('conditions', '')

        if '昨天' in time_desc:
            return TimeRange(
                start_date=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                end_date=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            )
        elif '最近7天' in time_desc or '过去一周' in time_desc:
            return TimeRange(
                relative_days=7
            )
        elif '最近30天' in time_desc or '过去一个月' in time_desc:
            return TimeRange(
                relative_days=30
            )

        return None

    def _parse_output_config(self, query: str, llm_analysis: Dict[str, Any]) -> OutputConfig:
        """解析输出配置"""
        config = OutputConfig()

        requirements = llm_analysis.get('output_requirements', '')

        if '图表' in requirements or 'chart' in requirements.lower():
            config.format = 'chart'
        elif 'csv' in requirements.lower():
            config.format = 'csv'

        # 解析限制数量
        import re
        numbers = re.findall(r'\d+', query)
        if numbers:
            config.limit = int(numbers[0])

        return config

    def _calculate_confidence(self, intent_result: IntentResult, llm_analysis: Dict[str, Any]) -> float:
        """计算综合置信度"""
        # 基于意图识别置信度和LLM分析质量计算
        intent_confidence = intent_result.confidence

        # 如果LLM分析包含关键信息，增加置信度
        llm_boost = 0.0
        if llm_analysis.get('data_entity'):
            llm_boost += 0.2
        if llm_analysis.get('conditions'):
            llm_boost += 0.1
        if llm_analysis.get('aggregations'):
            llm_boost += 0.1

        return min(intent_confidence + llm_boost, 1.0)

    def to_dict(self, analyzed_query: AnalyzedQuery) -> Dict[str, Any]:
        """将解析结果转换为字典"""
        result = {
            'original_query': analyzed_query.original_query,
            'intent': analyzed_query.intent_result.intent.value,
            'intent_confidence': analyzed_query.intent_result.confidence,
            'data_source': asdict(analyzed_query.data_source),
            'conditions': [asdict(cond) for cond in analyzed_query.conditions],
            'output_config': asdict(analyzed_query.output_config),
            'description': analyzed_query.description,
            'confidence_score': analyzed_query.confidence_score
        }

        if analyzed_query.aggregations:
            result['aggregations'] = asdict(analyzed_query.aggregations)

        if analyzed_query.time_range:
            result['time_range'] = asdict(analyzed_query.time_range)

        return result
