"""
引擎工厂
创建和管理不同类型的执行引擎
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from ..task.task_builder import DataTask


class ExecutionEngine(ABC):
    """执行引擎抽象基类"""

    def __init__(self, config: Dict[str, Any]):
        """初始化执行引擎"""
        self.config = config
        self.connected = False

    @abstractmethod
    def connect(self) -> bool:
        """连接到执行引擎"""
        pass

    @abstractmethod
    def disconnect(self):
        """断开连接"""
        pass

    @abstractmethod
    def execute_query(self, sql: str, task: DataTask) -> Dict[str, Any]:
        """执行SQL查询"""
        pass

    @abstractmethod
    def execute_count_query(self, sql: str, task: DataTask) -> int:
        """执行计数查询"""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        pass

    @abstractmethod
    def cancel_task(self, task_id: str):
        """取消任务"""
        pass


class EngineFactory:
    """执行引擎工厂"""

    _engines = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # 自动注册子类
        pass


# 在模块导入时注册引擎
def _register_engines():
    """注册所有可用的引擎"""
    try:
        from .spark_engine import SparkEngine
        EngineFactory.register_engine('spark', SparkEngine)
    except ImportError:
        pass

    try:
        from .hive_engine import HiveEngine
        EngineFactory.register_engine('hive', HiveEngine)
    except ImportError:
        pass

# 执行注册
_register_engines()

    @classmethod
    def register_engine(cls, engine_type: str, engine_class):
        """注册引擎类"""
        cls._engines[engine_type] = engine_class

    @classmethod
    def create_engine(cls, engine_type: str, config: Dict[str, Any]) -> ExecutionEngine:
        """
        创建执行引擎实例

        Args:
            engine_type: 引擎类型 (spark, hive, clickhouse, presto)
            config: 引擎配置

        Returns:
            ExecutionEngine: 执行引擎实例
        """
        if engine_type not in cls._engines:
            raise ValueError(f"不支持的引擎类型: {engine_type}")

        engine_class = cls._engines[engine_type]
        return engine_class(config)

    @classmethod
    def get_supported_engines(cls) -> list:
        """获取支持的引擎类型"""
        return list(cls._engines.keys())

    @classmethod
    def get_engine_config_template(cls, engine_type: str) -> Dict[str, Any]:
        """获取引擎配置模板"""
        templates = {
            'spark': {
                'master': 'yarn',
                'deploy_mode': 'cluster',
                'app_name': 'BigDataAgent',
                'executor_memory': '2g',
                'executor_cores': '2',
                'num_executors': '2',
                'queue': 'default'
            },
            'hive': {
                'host': 'localhost',
                'port': 10000,
                'auth_mechanism': 'PLAIN',
                'username': None,
                'password': None,
                'database': 'default'
            },
            'clickhouse': {
                'host': 'localhost',
                'port': 9000,
                'database': 'default',
                'username': 'default',
                'password': ''
            },
            'presto': {
                'host': 'localhost',
                'port': 8080,
                'catalog': 'hive',
                'schema': 'default',
                'username': None
            }
        }

        return templates.get(engine_type, {})
