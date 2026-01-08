import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    max_file_size: int = 10*1024*1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True,
    enable_file: bool = True
) -> None:
    """
    配置全局日志记录器。

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径，如果为None则使用默认路径
        max_file_size: 单个日志文件的最大大小（字节）
        backup_count: 保留的日志文件数量
        enable_console: 是否启用控制台日志
        enable_file: 是否启用文件日志
    """
    # 创建日志目录
    if enable_file and log_file is None:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"bigdata_agent_{timestamp}.log"

    # 创建格式化器
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 移除现有处理器（避免重复添加）
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 添加控制台处理器
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(simple_formatter)
        console_handler.setLevel(root_logger.level)
        root_logger.addHandler(console_handler)

    # 添加文件处理器
    if enable_file and log_file:
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(root_logger.level)
        root_logger.addHandler(file_handler)

        # 记录日志文件位置
        print(f"📝 日志文件: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    获取一个指定名称的日志记录器实例。

    Args:
        name (str): 通常是当前模块的名称 (__name__)。

    Returns:
        logging.Logger: 配置好的日志记录器实例。
    """
    return logging.getLogger(name)


# 性能日志装饰器
def log_performance(logger: Optional[logging.Logger] = None):
    """
    性能日志装饰器

    使用示例:
        @log_performance()
        def my_function():
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = logging.getLogger(func.__module__)

            start_time = datetime.now()
            logger.info(f"开始执行: {func.__name__}")

            try:
                result = func(*args, **kwargs)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                logger.info(f"执行完成: {func.__name__}, 耗时: {duration:.3f}秒")
                return result

            except Exception as e:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                logger.error(f"执行失败: {func.__name__}, 耗时: {duration:.3f}秒, 错误: {str(e)}")
                raise

        return wrapper
    return decorator


# 业务日志记录器
class BusinessLogger:
    """业务日志记录器"""

    def __init__(self, name: str = "business"):
        self.logger = get_logger(name)

    def log_query(self, user_query: str, intent: str = None, confidence: float = None):
        """记录用户查询"""
        self.logger.info(f"用户查询: '{user_query}' | 意图: {intent} | 置信度: {confidence:.2f}")

    def log_sql_generation(self, sql: str, dialect: str = "hive"):
        """记录SQL生成"""
        # 只记录SQL的前100个字符，避免日志过长
        sql_preview = sql[:100] + "..." if len(sql) > 100 else sql
        self.logger.info(f"生成SQL ({dialect}): {sql_preview}")

    def log_execution(self, task_id: str, sql: str, execution_time: float, row_count: int):
        """记录查询执行"""
        self.logger.info(f"任务执行完成: {task_id} | 耗时: {execution_time:.3f}s | 返回行数: {row_count}")

    def log_error(self, operation: str, error: str, context: Dict[str, Any] = None):
        """记录错误"""
        context_str = f" | 上下文: {context}" if context else ""
        self.logger.error(f"操作失败: {operation} | 错误: {error}{context_str}")

    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """记录性能指标"""
        details_str = f" | 详情: {details}" if details else ""
        self.logger.info(f"性能指标: {operation} | 耗时: {duration:.3f}s{details_str}")


# 全局业务日志记录器实例
business_logger = BusinessLogger()


# 初始化默认日志配置
setup_logging()


# 便捷函数
def info(message: str, *args, **kwargs):
    """记录INFO级别日志"""
    logging.info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs):
    """记录WARNING级别日志"""
    logging.warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs):
    """记录ERROR级别日志"""
    logging.error(message, *args, **kwargs)


def debug(message: str, *args, **kwargs):
    """记录DEBUG级别日志"""
    logging.debug(message, *args, **kwargs)


def critical(message: str, *args, **kwargs):
    """记录CRITICAL级别日志"""
    logging.critical(message, *args, **kwargs)