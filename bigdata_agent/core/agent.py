"""
大数据处理Agent核心类
集成所有组件，提供统一的查询处理接口
"""

import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..nlp.query_analyzer import QueryAnalyzer
from ..task.task_builder import TaskBuilder
from ..execution.engine_factory import EngineFactory
from ..result.result_processor import ResultProcessor


class BigDataAgent:
    """大数据处理智能代理"""

    def __init__(self, engine_type: str = "spark", engine_config: Optional[Dict[str, Any]] = None):
        """
        初始化大数据Agent

        Args:
            engine_type: 执行引擎类型 (spark, hive, clickhouse, presto)
            engine_config: 引擎配置，如果为None则使用默认配置
        """
        self.engine_type = engine_type
        self.engine_config = engine_config or EngineFactory.get_engine_config_template(engine_type)

        # 初始化组件
        self.query_analyzer = QueryAnalyzer()
        self.task_builder = TaskBuilder()
        self.result_processor = ResultProcessor()
        self.execution_engine = None

        # 连接状态
        self.connected = False

        self.logger = logging.getLogger(__name__)
        self.business_logger = logging.getLogger("business")

        # 确保business logger有处理器
        if not self.business_logger.handlers:
            from config.logging_config import setup_logging
            # 如果还没有设置日志，先设置一下
            if not logging.getLogger().handlers:
                setup_logging()

        print("🤖 BigData Agent初始化完成")
        print(f"   执行引擎: {engine_type}")

        self.logger.info(f"BigData Agent初始化完成，执行引擎: {engine_type}")

    def connect(self) -> bool:
        """
        连接到执行引擎

        Returns:
            bool: 连接是否成功
        """
        try:
            self.execution_engine = EngineFactory.create_engine(self.engine_type, self.engine_config)
            self.connected = self.execution_engine.connect()

            if self.connected:
                print("✅ 执行引擎连接成功")
            else:
                print("❌ 执行引擎连接失败")
            return self.connected

        except Exception as e:
            print(f"❌ 连接执行引擎失败: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """断开执行引擎连接"""
        if self.execution_engine:
            self.execution_engine.disconnect()
            self.execution_engine = None
        self.connected = False
        print("✅ 执行引擎已断开连接")

    def query(self, user_query: str, output_format: str = "json", **kwargs) -> Dict[str, Any]:
        """
        执行用户查询

        Args:
            user_query: 用户的自然语言查询
            output_format: 输出格式 (json, csv, chart, table)
            **kwargs: 额外参数

        Returns:
            dict: 查询结果
        """
        if not self.connected:
            return {
                'success': False,
                'error': '执行引擎未连接，请先调用 connect()',
                'timestamp': datetime.now().isoformat()
            }

        start_time = time.time()

        try:
            # 记录用户查询
            self.business_logger.info(f"用户查询: '{user_query}'")

            # 1. NLP分析查询
            print(f"🔍 分析查询: {user_query}")
            self.logger.debug(f"开始分析查询: {user_query}")

            analyzed_query = self.query_analyzer.analyze_query(user_query)

            intent_result = analyzed_query.intent_result
            print(f"   识别意图: {intent_result.intent.value}")
            print(f"   数据源: {analyzed_query.data_source.table}")
            print(".2f")

            # 记录意图识别结果
            self.business_logger.info(
                f"意图识别: '{user_query}' -> {intent_result.intent.value} (置信度: {intent_result.confidence:.2f})"
            )

            # 2. 构建执行任务
            print("🏗️ 构建执行任务")
            task = self.task_builder.build_task(
                analyzed_query=analyzed_query,
                engine_type=self.engine_type,
                priority=kwargs.get('priority', 1),
                timeout_seconds=kwargs.get('timeout', 3600)
            )

            print(f"   任务ID: {task.task_config.task_id}")
            print(f"   SQL: {task.sql_query[:100]}...")

            # 记录SQL生成
            self.business_logger.info(f"生成SQL ({self.engine_type}): {task.sql_query[:100]}...")

            # 3. 执行查询
            print("⚡ 执行查询")
            execution_start = time.time()
            execution_result = self.execution_engine.execute_query(task.sql_query, task)
            execution_time = time.time() - execution_start
            print(".2f")

            # 记录执行结果
            if execution_result.get('success'):
                self.business_logger.info(
                    f"任务执行完成: {task.task_config.task_id} | 耗时: {execution_time:.3f}s | 返回行数: {execution_result.get('row_count', 0)}"
                )
            else:
                self.business_logger.error(
                    f"任务执行失败: {task.task_config.task_id} | 耗时: {execution_time:.3f}s | 错误: {execution_result.get('error', '未知错误')}"
                )
            # 4. 处理结果
            print("📊 处理结果")
            processed_result = self.result_processor.process_result(
                execution_result=execution_result,
                analyzed_query=analyzed_query,
                output_format=output_format,
                **kwargs
            )

            # 添加额外的元信息
            processed_result['query_info'] = {
                'original_query': user_query,
                'analyzed_query': self.query_analyzer.to_dict(analyzed_query),
                'task_info': task.to_dict(),
                'total_time': execution_time
            }

            if processed_result.get('success'):
                print("✅ 查询执行成功")
            else:
                print(f"❌ 查询执行失败: {processed_result.get('error')}")

            return processed_result

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"查询处理失败: {str(e)}"

            print(f"❌ {error_msg}")

            return {
                'success': False,
                'error': error_msg,
                'timestamp': datetime.now().isoformat(),
                'execution_time': execution_time
            }

    def preview_query(self, user_query: str, sample_size: int = 5) -> Dict[str, Any]:
        """
        预览查询结果（采样）

        Args:
            user_query: 用户查询
            sample_size: 采样大小

        Returns:
            dict: 预览结果
        """
        if not self.connected:
            return {'success': False, 'error': '执行引擎未连接'}

        try:
            # 分析查询
            analyzed_query = self.query_analyzer.analyze_query(user_query)

            # 构建采样任务
            task = self.task_builder.build_task(analyzed_query, self.engine_type)

            # 执行采样查询
            if task.sample_sql:
                execution_result = self.execution_engine.execute_query(task.sample_sql, task)
                processed_result = self.result_processor.process_result(
                    execution_result, analyzed_query, 'table'
                )

                return {
                    'success': True,
                    'preview_data': processed_result.get('data', {}),
                    'sample_size': sample_size,
                    'total_estimated': '未知'  # 可以通过count_sql获取
                }
            else:
                return {'success': False, 'error': '无法生成采样查询'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_status(self) -> Dict[str, Any]:
        """获取Agent状态"""
        status = {
            'connected': self.connected,
            'engine_type': self.engine_type,
            'timestamp': datetime.now().isoformat()
        }

        if self.execution_engine:
            status['engine_status'] = self.execution_engine.get_status()
        else:
            status['engine_status'] = {'connected': False}

        return status

    def list_supported_engines(self) -> List[str]:
        """列出支持的执行引擎"""
        return EngineFactory.get_supported_engines()

    def estimate_query_cost(self, user_query: str) -> Dict[str, Any]:
        """
        估算查询成本

        Returns:
            dict: 成本估算信息
        """
        try:
            analyzed_query = self.query_analyzer.analyze_query(user_query)
            task = self.task_builder.build_task(analyzed_query, self.engine_type)

            estimation = self.task_builder.estimate_execution_time(task)

            # 获取数据量估算
            if self.connected and task.count_sql:
                count_result = self.execution_engine.execute_count_query(task.count_sql, task)
                estimation['estimated_row_count'] = count_result
            else:
                estimation['estimated_row_count'] = '未知'

            return {
                'success': True,
                'estimation': estimation,
                'query_complexity': self.task_builder._calculate_complexity(analyzed_query)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def batch_query(self, queries: List[str], output_format: str = "json") -> List[Dict[str, Any]]:
        """
        批量执行查询

        Args:
            queries: 查询列表
            output_format: 输出格式

        Returns:
            list: 查询结果列表
        """
        results = []

        for i, query in enumerate(queries, 1):
            print(f"\n📝 执行查询 {i}/{len(queries)}")
            result = self.query(query, output_format)
            result['batch_index'] = i
            results.append(result)

        return results

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
