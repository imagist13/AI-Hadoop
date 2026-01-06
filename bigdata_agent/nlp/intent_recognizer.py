"""
意图识别器
识别用户查询的意图类型
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass


class QueryIntent(Enum):
    """查询意图类型枚举"""
    STATISTICS = "statistics"          # 统计查询
    ANALYSIS = "analysis"             # 分析查询
    TREND = "trend"                   # 趋势分析
    COMPARISON = "comparison"         # 对比分析
    FILTER = "filter"                 # 筛选查询
    AGGREGATION = "aggregation"       # 聚合查询
    RANKING = "ranking"              # 排名查询
    DISTRIBUTION = "distribution"    # 分布查询
    CORRELATION = "correlation"      # 相关性分析
    UNKNOWN = "unknown"              # 未知意图


@dataclass
class IntentResult:
    """意图识别结果"""
    intent: QueryIntent
    confidence: float
    parameters: Dict[str, Any]
    raw_query: str


class IntentRecognizer:
    """意图识别器类"""

    def __init__(self):
        """初始化意图识别器"""
        # 意图关键词映射
        self.intent_keywords = {
            QueryIntent.STATISTICS: [
                '统计', '统计数', '数量', '总数', '总计', 'count', 'sum', '统计数据'
            ],
            QueryIntent.ANALYSIS: [
                '分析', '分析数据', '数据分析', '深入分析', '详细分析'
            ],
            QueryIntent.TREND: [
                '趋势', '变化趋势', '发展趋势', '时间趋势', '历史趋势'
            ],
            QueryIntent.COMPARISON: [
                '对比', '比较', '对比分析', '差异', '差距', '对比不同'
            ],
            QueryIntent.FILTER: [
                '筛选', '过滤', '查找', '查询', '搜索', 'where', '筛选出'
            ],
            QueryIntent.AGGREGATION: [
                '聚合', '汇总', '分组汇总', 'group by', '分组统计'
            ],
            QueryIntent.RANKING: [
                '排名', '排序', 'top', '前几名', '排名靠前', '最', '第'
            ],
            QueryIntent.DISTRIBUTION: [
                '分布', '分布情况', '分布分析', '占比', '比例'
            ],
            QueryIntent.CORRELATION: [
                '相关性', '相关', '关联', '关系', '相关分析'
            ]
        }

        # 时间关键词
        self.time_keywords = [
            '今天', '昨天', '最近', '过去', '未来', '本周', '上周', '本月', '上月',
            '今年', '去年', '最近7天', '最近30天', '过去一周', '过去一个月'
        ]

        # 聚合关键词
        self.aggregation_keywords = [
            '求和', '平均', '最大', '最小', '计数', '总计', '均值', '平均值'
        ]

    def recognize_intent(self, query: str) -> IntentResult:
        """
        识别查询意图

        Args:
            query: 用户查询字符串

        Returns:
            IntentResult: 意图识别结果
        """
        query_lower = query.lower()

        # 计算每个意图的匹配分数
        intent_scores = {}
        for intent, keywords in self.intent_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    score += 1
            intent_scores[intent] = score

        # 找到最高分的意图
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = intent_scores[best_intent] / max(1, len(self.intent_keywords[best_intent]))

        # 如果没有匹配到任何关键词，默认使用统计意图
        if confidence == 0:
            best_intent = QueryIntent.STATISTICS
            confidence = 0.5

        # 提取参数
        parameters = self._extract_parameters(query)

        return IntentResult(
            intent=best_intent,
            confidence=min(confidence, 1.0),
            parameters=parameters,
            raw_query=query
        )

    def _extract_parameters(self, query: str) -> Dict[str, Any]:
        """提取查询参数"""
        parameters = {}

        # 提取时间相关参数
        for time_kw in self.time_keywords:
            if time_kw in query:
                parameters['time_range'] = time_kw
                break

        # 提取聚合函数
        for agg_kw in self.aggregation_keywords:
            if agg_kw in query:
                parameters['aggregation'] = agg_kw
                break

        # 提取数字（可能表示限制数量）
        import re
        numbers = re.findall(r'\d+', query)
        if numbers:
            parameters['limit'] = int(numbers[0])

        # 提取可能的字段名（简单识别）
        # 这里可以根据具体的数据模式进行更复杂的识别
        if '用户' in query:
            parameters['entity'] = 'user'
        elif '订单' in query:
            parameters['entity'] = 'order'
        elif '商品' in query:
            parameters['entity'] = 'product'

        return parameters

    def get_intent_description(self, intent: QueryIntent) -> str:
        """获取意图的中文描述"""
        descriptions = {
            QueryIntent.STATISTICS: "统计查询",
            QueryIntent.ANALYSIS: "数据分析",
            QueryIntent.TREND: "趋势分析",
            QueryIntent.COMPARISON: "对比分析",
            QueryIntent.FILTER: "数据筛选",
            QueryIntent.AGGREGATION: "数据聚合",
            QueryIntent.RANKING: "排名查询",
            QueryIntent.DISTRIBUTION: "分布分析",
            QueryIntent.CORRELATION: "相关性分析",
            QueryIntent.UNKNOWN: "未知查询"
        }
        return descriptions.get(intent, "未知查询")
