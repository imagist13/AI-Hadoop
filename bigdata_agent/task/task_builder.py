"""
任务构建器
将分析结果和SQL组合成完整的执行任务
"""

import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

from ..nlp.query_analyzer import AnalyzedQuery
from .sql_generator import SQLGenerator


@dataclass
class TaskConfig:
    """任务配置"""
    task_id: str
    task_type: str  # query, analysis, export, etc.
    priority: int = 1  # 1-5, 5最高
    timeout_seconds: int = 3600  # 默认1小时超时
    retry_count: int = 0
    retry_delay: int = 60  # 重试间隔秒数


@dataclass
class ExecutionContext:
    """执行上下文"""
    engine_type: str = "spark"  # spark, hive, clickhouse, presto
    cluster_config: Dict[str, Any] = None
    resource_limits: Dict[str, Any] = None

    def __post_init__(self):
        if self.cluster_config is None:
            self.cluster_config = {}
        if self.resource_limits is None:
            self.resource_limits = {
                'memory_gb': 4,
                'cores': 2,
                'executor_instances': 2
            }


@dataclass
class DataTask:
    """数据处理任务"""
    task_config: TaskConfig
    analyzed_query: AnalyzedQuery
    execution_context: ExecutionContext
    sql_query: str
    count_sql: Optional[str] = None
    sample_sql: Optional[str] = None
    created_at: str = ""
    status: str = "pending"  # pending, running, completed, failed, cancelled

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'task_config': asdict(self.task_config),
            'analyzed_query': self.analyzed_query.nlp.query_analyzer.to_dict(self.analyzed_query),
            'execution_context': asdict(self.execution_context),
            'sql_query': self.sql_query,
            'count_sql': self.count_sql,
            'sample_sql': self.sample_sql,
            'created_at': self.created_at,
            'status': self.status
        }


class TaskBuilder:
    """任务构建器"""

    def __init__(self):
        """初始化任务构建器"""
        self.sql_generator = SQLGenerator()

    def build_task(self, analyzed_query: AnalyzedQuery,
                  engine_type: str = "spark",
                  priority: int = 1,
                  timeout_seconds: int = 3600) -> DataTask:
        """
        构建数据处理任务

        Args:
            analyzed_query: 解析后的查询结构
            engine_type: 执行引擎类型
            priority: 任务优先级
            timeout_seconds: 超时时间

        Returns:
            DataTask: 完整的数据处理任务
        """
        # 生成任务ID
        task_id = str(uuid.uuid4())

        # 创建任务配置
        task_config = TaskConfig(
            task_id=task_id,
            task_type=self._determine_task_type(analyzed_query),
            priority=priority,
            timeout_seconds=timeout_seconds
        )

        # 创建执行上下文
        execution_context = ExecutionContext(
            engine_type=engine_type,
            cluster_config=self._get_cluster_config(engine_type),
            resource_limits=self._get_resource_limits(analyzed_query, engine_type)
        )

        # 生成SQL查询
        sql_query = self.sql_generator.generate_sql(analyzed_query, engine_type)

        # 生成计数SQL（用于估算结果大小）
        count_sql = self.sql_generator.generate_count_sql(analyzed_query, engine_type)

        # 生成采样SQL（用于数据预览）
        sample_sql = self.sql_generator.generate_sample_sql(analyzed_query, sample_size=5, dialect=engine_type)

        # 验证SQL
        validation_result = self.sql_generator.validate_sql(sql_query, engine_type)
        if not validation_result['valid']:
            raise ValueError(f"生成的SQL无效: {validation_result['errors']}")

        return DataTask(
            task_config=task_config,
            analyzed_query=analyzed_query,
            execution_context=execution_context,
            sql_query=sql_query,
            count_sql=count_sql,
            sample_sql=sample_sql
        )

    def _determine_task_type(self, analyzed_query: AnalyzedQuery) -> str:
        """确定任务类型"""
        intent = analyzed_query.intent_result.intent.value

        # 根据意图映射任务类型
        type_mapping = {
            'statistics': 'query',
            'analysis': 'analysis',
            'trend': 'analysis',
            'comparison': 'analysis',
            'filter': 'query',
            'aggregation': 'aggregation',
            'ranking': 'query',
            'distribution': 'analysis',
            'correlation': 'analysis'
        }

        return type_mapping.get(intent, 'query')

    def _get_cluster_config(self, engine_type: str) -> Dict[str, Any]:
        """获取集群配置"""
        # 这里可以从配置文件加载具体的集群配置
        configs = {
            'spark': {
                'master': 'yarn',
                'deploy_mode': 'cluster',
                'queue': 'default'
            },
            'hive': {
                'connection_url': 'thrift://localhost:10000',
                'auth_mechanism': 'PLAIN'
            },
            'clickhouse': {
                'host': 'localhost',
                'port': 9000,
                'database': 'default'
            },
            'presto': {
                'host': 'localhost',
                'port': 8080,
                'catalog': 'hive',
                'schema': 'default'
            }
        }

        return configs.get(engine_type, {})

    def _get_resource_limits(self, analyzed_query: AnalyzedQuery, engine_type: str) -> Dict[str, Any]:
        """根据查询复杂度确定资源限制"""
        # 基础资源配置
        base_limits = {
            'memory_gb': 2,
            'cores': 1,
            'executor_instances': 1
        }

        # 根据查询复杂度调整资源
        complexity_factor = self._calculate_complexity(analyzed_query)

        if complexity_factor > 1:
            base_limits['memory_gb'] = min(base_limits['memory_gb'] * complexity_factor, 16)
            base_limits['cores'] = min(base_limits['cores'] * complexity_factor, 8)
            base_limits['executor_instances'] = min(base_limits['executor_instances'] * complexity_factor, 4)

        return base_limits

    def _calculate_complexity(self, analyzed_query: AnalyzedQuery) -> float:
        """计算查询复杂度因子"""
        factor = 1.0

        # 条件数量影响复杂度
        if len(analyzed_query.conditions) > 3:
            factor *= 1.5

        # 聚合操作增加复杂度
        if analyzed_query.aggregations:
            factor *= 2.0
            if len(analyzed_query.aggregations.group_by) > 2:
                factor *= 1.5

        # 时间范围查询增加复杂度
        if analyzed_query.time_range and analyzed_query.time_range.relative_days:
            if analyzed_query.time_range.relative_days > 30:
                factor *= 1.2

        # 分析型查询复杂度更高
        intent = analyzed_query.intent_result.intent.value
        if intent in ['analysis', 'trend', 'correlation']:
            factor *= 1.5

        return min(factor, 5.0)  # 最大5倍

    def build_batch_tasks(self, queries: List[str],
                         engine_type: str = "spark",
                         priority: int = 1) -> List[DataTask]:
        """
        批量构建任务

        Args:
            queries: 查询列表
            engine_type: 执行引擎类型
            priority: 任务优先级

        Returns:
            List[DataTask]: 任务列表
        """
        from ..nlp.query_analyzer import QueryAnalyzer

        analyzer = QueryAnalyzer()
        tasks = []

        for query in queries:
            try:
                analyzed_query = analyzer.analyze_query(query)
                task = self.build_task(analyzed_query, engine_type, priority)
                tasks.append(task)
            except Exception as e:
                print(f"构建任务失败: {query}, 错误: {e}")
                continue

        return tasks

    def estimate_execution_time(self, task: DataTask) -> Dict[str, Any]:
        """
        估算任务执行时间

        Returns:
            dict: 包含估算时间和影响因子的信息
        """
        base_time = 30  # 基础执行时间（秒）

        # 复杂度因子
        complexity_factor = self._calculate_complexity(task.analyzed_query)

        # 引擎因子
        engine_factors = {
            'spark': 1.0,
            'hive': 1.5,
            'clickhouse': 0.8,
            'presto': 1.2
        }
        engine_factor = engine_factors.get(task.execution_context.engine_type, 1.0)

        # 资源因子（更多资源通常执行更快）
        resource_factor = 1.0
        cores = task.execution_context.resource_limits.get('cores', 1)
        memory = task.execution_context.resource_limits.get('memory_gb', 2)
        resource_factor = 1.0 / (cores * memory / 4)  # 基准是2核4G

        estimated_seconds = base_time * complexity_factor * engine_factor * resource_factor

        return {
            'estimated_seconds': estimated_seconds,
            'estimated_minutes': estimated_seconds / 60,
            'complexity_factor': complexity_factor,
            'engine_factor': engine_factor,
            'resource_factor': resource_factor,
            'confidence': 'medium'  # low, medium, high
        }
