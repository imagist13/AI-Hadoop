"""
Spark执行引擎
使用PySpark执行SQL查询
"""

import time
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from pyspark.sql import SparkSession
    from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, DateType
    SPARK_AVAILABLE = True
except ImportError:
    SPARK_AVAILABLE = False

from .engine_factory import ExecutionEngine
from ..task.task_builder import DataTask


class SparkEngine(ExecutionEngine):
    """Spark执行引擎"""

    def __init__(self, config: Dict[str, Any]):
        """初始化Spark引擎"""
        super().__init__(config)
        self.spark_session: Optional[SparkSession] = None
        self.executor = ThreadPoolExecutor(max_workers=2)

        if not SPARK_AVAILABLE:
            raise ImportError("PySpark不可用，请安装pyspark: pip install pyspark")

    def connect(self) -> bool:
        """连接到Spark集群"""
        try:
            if self.spark_session:
                self.spark_session.stop()

            builder = SparkSession.builder.appName(
                self.config.get('app_name', 'BigDataAgent')
            )

            # 配置Spark
            master = self.config.get('master', 'local[*]')
            if master != 'local[*]':
                builder = builder.master(master)

            # YARN配置
            if master == 'yarn':
                builder = builder.config('spark.submit.deployMode',
                                       self.config.get('deploy_mode', 'client'))

            # 资源配置
            executor_memory = self.config.get('executor_memory', '2g')
            executor_cores = self.config.get('executor_cores', '2')
            num_executors = self.config.get('num_executors', '2')

            builder = builder \
                .config('spark.executor.memory', executor_memory) \
                .config('spark.executor.cores', executor_cores) \
                .config('spark.executor.instances', num_executors)

            # 队列配置
            queue = self.config.get('queue', 'default')
            if queue != 'default':
                builder = builder.config('spark.yarn.queue', queue)

            # 其他配置
            builder = builder \
                .config('spark.sql.adaptive.enabled', 'true') \
                .config('spark.sql.adaptive.coalescePartitions.enabled', 'true') \
                .config('spark.serializer', 'org.apache.spark.serializer.KryoSerializer')

            self.spark_session = builder.getOrCreate()
            self.connected = True

            print(f"✅ Spark连接成功 - Master: {master}")
            return True

        except Exception as e:
            print(f"❌ Spark连接失败: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """断开Spark连接"""
        if self.spark_session:
            try:
                self.spark_session.stop()
                print("✅ Spark连接已断开")
            except Exception as e:
                print(f"⚠️ Spark断开连接时出错: {e}")
            finally:
                self.spark_session = None
                self.connected = False

    def execute_query(self, sql: str, task: DataTask) -> Dict[str, Any]:
        """
        执行SQL查询

        Returns:
            dict: 包含执行结果、状态、统计信息
        """
        if not self.connected or not self.spark_session:
            return {
                'success': False,
                'error': 'Spark未连接',
                'data': None,
                'row_count': 0,
                'execution_time': 0
            }

        start_time = time.time()

        try:
            # 执行查询
            df = self.spark_session.sql(sql)

            # 获取结果
            # 注意：在生产环境中，应该考虑内存限制和分页
            result_data = df.collect()

            # 转换为字典格式
            columns = df.columns
            data = [row.asDict() for row in result_data]

            execution_time = time.time() - start_time

            return {
                'success': True,
                'error': None,
                'data': data,
                'columns': columns,
                'row_count': len(data),
                'execution_time': execution_time,
                'task_id': task.task_config.task_id
            }

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"SQL执行失败: {str(e)}"

            print(f"❌ {error_msg}")
            print(f"   SQL: {sql}")

            return {
                'success': False,
                'error': error_msg,
                'data': None,
                'row_count': 0,
                'execution_time': execution_time,
                'task_id': task.task_config.task_id
            }

    def execute_count_query(self, sql: str, task: DataTask) -> int:
        """执行计数查询"""
        if not self.connected or not self.spark_session:
            return 0

        try:
            df = self.spark_session.sql(sql)
            result = df.collect()
            if result:
                return result[0][0]  # 第一行第一列
            return 0
        except Exception as e:
            print(f"计数查询失败: {e}")
            return 0

    def execute_async(self, sql: str, task: DataTask, callback=None):
        """异步执行查询"""
        future = self.executor.submit(self.execute_query, sql, task)

        if callback:
            future.add_done_callback(lambda f: callback(f.result()))

        return future

    def get_status(self) -> Dict[str, Any]:
        """获取Spark状态"""
        if not self.spark_session:
            return {'connected': False, 'version': None, 'master': None}

        try:
            version = self.spark_session.version
            master = self.spark_session.sparkContext.master
            app_id = self.spark_session.sparkContext.applicationId

            return {
                'connected': self.connected,
                'version': version,
                'master': master,
                'app_id': app_id,
                'executors': len(self.spark_session.sparkContext.statusTracker().getExecutorInfos())
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }

    def cancel_task(self, task_id: str):
        """取消任务（Spark中较难实现精确取消）"""
        print(f"⚠️ Spark任务取消功能有限: {task_id}")
        # 在实际实现中，可能需要通过YARN REST API或其他方式取消

    def create_table_from_csv(self, table_name: str, csv_path: str,
                            schema: Optional[Dict[str, str]] = None) -> bool:
        """
        从CSV文件创建临时表

        Args:
            table_name: 表名
            csv_path: CSV文件路径
            schema: 字段类型映射，如 {'name': 'string', 'age': 'int'}
        """
        try:
            # 读取CSV
            df = self.spark_session.read.csv(csv_path, header=True, inferSchema=True)

            # 如果提供了schema，进行类型转换
            if schema:
                for col_name, col_type in schema.items():
                    if col_name in df.columns:
                        df = df.withColumn(col_name, df[col_name].cast(col_type))

            # 创建临时视图
            df.createOrReplaceTempView(table_name)
            print(f"✅ 已创建临时表: {table_name}")
            return True

        except Exception as e:
            print(f"❌ 创建表失败: {e}")
            return False

    def list_tables(self) -> list:
        """列出所有临时表"""
        if not self.spark_session:
            return []

        try:
            return self.spark_session.catalog.listTables()
        except Exception:
            return []

    def get_table_schema(self, table_name: str) -> Optional[Dict[str, Any]]:
        """获取表结构"""
        if not self.spark_session:
            return None

        try:
            df = self.spark_session.table(table_name)
            schema = df.schema

            return {
                'table_name': table_name,
                'columns': [
                    {
                        'name': field.name,
                        'type': str(field.dataType),
                        'nullable': field.nullable
                    }
                    for field in schema.fields
                ]
            }
        except Exception as e:
            print(f"获取表结构失败: {e}")
            return None
