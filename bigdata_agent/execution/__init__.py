"""
执行引擎模块
负责调用底层大数据处理框架执行任务
"""

from .engine_factory import EngineFactory
from .spark_engine import SparkEngine
from .hive_engine import HiveEngine

# 注册引擎
EngineFactory.register_engine('spark', SparkEngine)
EngineFactory.register_engine('hive', HiveEngine)

__all__ = ['EngineFactory', 'SparkEngine', 'HiveEngine']
