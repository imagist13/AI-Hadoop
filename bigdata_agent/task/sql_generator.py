"""
SQL生成器
根据分析结果生成SQL/HQL查询语句
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ..nlp.query_analyzer import AnalyzedQuery, DataSource, QueryCondition, AggregationConfig, TimeRange


class SQLGenerator:
    """SQL查询生成器"""

    def __init__(self):
        """初始化SQL生成器"""
        self.logger = logging.getLogger(__name__)
        self.supported_dialects = ['hive', 'spark', 'clickhouse', 'presto']

    def generate_sql(self, analyzed_query: AnalyzedQuery, dialect: str = 'hive') -> str:
        """
        生成SQL查询语句

        Args:
            analyzed_query: 解析后的查询结构
            dialect: SQL方言 (hive, spark, clickhouse, presto)

        Returns:
            str: 生成的SQL查询语句
        """
        self.logger.info(f"开始生成SQL (方言: {dialect})")

        if dialect not in self.supported_dialects:
            self.logger.warning(f"不支持的方言 '{dialect}'，使用默认方言 'hive'")
            dialect = 'hive'

        # 构建SELECT子句
        select_clause = self._build_select_clause(analyzed_query)

        # 构建FROM子句
        from_clause = self._build_from_clause(analyzed_query.data_source, dialect)

        # 构建WHERE子句
        where_clause = self._build_where_clause(analyzed_query.conditions, analyzed_query.time_range)

        # 构建GROUP BY子句
        group_by_clause = self._build_group_by_clause(analyzed_query.aggregations)

        # 构建ORDER BY子句
        order_by_clause = self._build_order_by_clause(analyzed_query.output_config)

        # 构建LIMIT子句
        limit_clause = self._build_limit_clause(analyzed_query.output_config)

        # 组合完整SQL
        sql_parts = [select_clause, from_clause]
        if where_clause:
            sql_parts.append(f"WHERE {where_clause}")
        if group_by_clause:
            sql_parts.append(f"GROUP BY {group_by_clause}")
        if order_by_clause:
            sql_parts.append(f"ORDER BY {order_by_clause}")
        if limit_clause:
            sql_parts.append(f"LIMIT {limit_clause}")

        return " ".join(sql_parts)

    def _build_select_clause(self, analyzed_query: AnalyzedQuery) -> str:
        """构建SELECT子句"""
        if analyzed_query.aggregations:
            # 有聚合操作
            select_fields = []

            # 添加聚合字段
            for field, func in analyzed_query.aggregations.aggregations.items():
                select_fields.append(f"{func} as {field}")

            # 添加分组字段
            for group_field in analyzed_query.aggregations.group_by:
                if group_field not in [f.split(' as ')[-1] for f in select_fields]:
                    select_fields.append(group_field)

            return f"SELECT {', '.join(select_fields)}"
        else:
            # 无聚合操作，默认选择所有字段或关键字段
            if analyzed_query.data_source.type == 'hive':
                return "SELECT *"
            else:
                # 对于其他数据源，可以根据数据字典选择合适的字段
                return "SELECT *"

    def _build_from_clause(self, data_source: DataSource, dialect: str) -> str:
        """构建FROM子句"""
        if data_source.database and dialect in ['hive', 'spark']:
            table_ref = f"{data_source.database}.{data_source.table}"
        else:
            table_ref = data_source.table

        return f"FROM {table_ref}"

    def _build_where_clause(self, conditions: List[QueryCondition],
                           time_range: Optional[TimeRange]) -> Optional[str]:
        """构建WHERE子句"""
        where_conditions = []

        # 添加查询条件
        for condition in conditions:
            cond_str = self._condition_to_sql(condition)
            if cond_str:
                where_conditions.append(cond_str)

        # 添加时间范围条件
        if time_range:
            time_cond = self._time_range_to_sql(time_range)
            if time_cond:
                where_conditions.append(time_cond)

        return " AND ".join(where_conditions) if where_conditions else None

    def _build_group_by_clause(self, aggregations: Optional[AggregationConfig]) -> Optional[str]:
        """构建GROUP BY子句"""
        if aggregations and aggregations.group_by:
            return ", ".join(aggregations.group_by)
        return None

    def _build_order_by_clause(self, output_config) -> Optional[str]:
        """构建ORDER BY子句"""
        if output_config.sort_by:
            order = output_config.sort_order.upper()
            return f"{output_config.sort_by} {order}"
        return None

    def _build_limit_clause(self, output_config) -> Optional[str]:
        """构建LIMIT子句"""
        if output_config.limit:
            return str(output_config.limit)
        return None

    def _condition_to_sql(self, condition: QueryCondition) -> str:
        """将查询条件转换为SQL"""
        operator_map = {
            '=': '=',
            '>': '>',
            '<': '<',
            '>=': '>=',
            '<=': '<=',
            'like': 'LIKE',
            'in': 'IN',
            'between': 'BETWEEN'
        }

        op = operator_map.get(condition.operator, '=')

        if op == 'IN':
            if isinstance(condition.value, list):
                value_str = f"({', '.join(repr(v) for v in condition.value)})"
            else:
                value_str = f"({condition.value})"
        elif op == 'BETWEEN':
            if isinstance(condition.value, (list, tuple)) and len(condition.value) == 2:
                value_str = f"{condition.value[0]} AND {condition.value[1]}"
            else:
                value_str = str(condition.value)
        else:
            value_str = repr(condition.value)

        return f"{condition.field} {op} {value_str}"

    def _time_range_to_sql(self, time_range: TimeRange) -> Optional[str]:
        """将时间范围转换为SQL条件"""
        conditions = []

        if time_range.relative_days:
            # 相对天数
            start_date = (datetime.now() - timedelta(days=time_range.relative_days)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            conditions.append(f"date >= '{start_date}'")
            conditions.append(f"date <= '{end_date}'")
        else:
            # 绝对日期范围
            if time_range.start_date:
                conditions.append(f"date >= '{time_range.start_date}'")
            if time_range.end_date:
                conditions.append(f"date <= '{time_range.end_date}'")

        return " AND ".join(conditions) if conditions else None

    def generate_count_sql(self, analyzed_query: AnalyzedQuery, dialect: str = 'hive') -> str:
        """生成计数查询SQL（用于预估结果数量）"""
        from_clause = self._build_from_clause(analyzed_query.data_source, dialect)
        where_clause = self._build_where_clause(analyzed_query.conditions, analyzed_query.time_range)

        sql = f"SELECT COUNT(*) as total_count {from_clause}"
        if where_clause:
            sql += f" WHERE {where_clause}"

        return sql

    def generate_sample_sql(self, analyzed_query: AnalyzedQuery, sample_size: int = 10,
                           dialect: str = 'hive') -> str:
        """生成采样查询SQL（用于预览数据）"""
        select_clause = self._build_select_clause(analyzed_query)
        from_clause = self._build_from_clause(analyzed_query.data_source, dialect)
        where_clause = self._build_where_clause(analyzed_query.conditions, analyzed_query.time_range)

        sql = f"{select_clause} {from_clause}"
        if where_clause:
            sql += f" WHERE {where_clause}"

        sql += f" LIMIT {sample_size}"
        return sql

    def validate_sql(self, sql: str, dialect: str = 'hive') -> Dict[str, Any]:
        """
        验证SQL语法（基础验证）

        Returns:
            dict: 包含验证结果和建议
        """
        result = {
            'valid': True,
            'warnings': [],
            'errors': []
        }

        # 基础语法检查
        sql_upper = sql.upper()

        # 检查是否有基本的SELECT语句
        if not sql_upper.strip().startswith('SELECT'):
            result['valid'] = False
            result['errors'].append('SQL必须以SELECT开头')

        # 检查是否有FROM子句
        if 'FROM' not in sql_upper:
            result['valid'] = False
            result['errors'].append('缺少FROM子句')

        # 检查括号匹配
        if sql.count('(') != sql.count(')'):
            result['valid'] = False
            result['errors'].append('括号不匹配')

        # 检查引号匹配
        single_quotes = sql.count("'")
        if single_quotes % 2 != 0:
            result['warnings'].append('单引号可能不匹配')

        return result
