"""
Hive执行引擎
通过PyHive或impyla连接Hive执行查询
"""

import time
from typing import Dict, Any, Optional

try:
    from pyhive import hive
    HIVE_AVAILABLE = True
except ImportError:
    HIVE_AVAILABLE = False

from .engine_factory import ExecutionEngine
from ..task.task_builder import DataTask


class HiveEngine(ExecutionEngine):
    """Hive执行引擎"""

    def __init__(self, config: Dict[str, Any]):
        """初始化Hive引擎"""
        super().__init__(config)
        self.connection = None

        if not HIVE_AVAILABLE:
            raise ImportError("PyHive不可用，请安装: pip install pyhive[hive]")

    def connect(self) -> bool:
        """连接到Hive"""
        try:
            if self.connection:
                self.connection.close()

            self.connection = hive.Connection(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 10000),
                username=self.config.get('username'),
                password=self.config.get('password'),
                auth_mechanism=self.config.get('auth_mechanism', 'PLAIN'),
                database=self.config.get('database', 'default')
            )

            self.connected = True
            print("✅ Hive连接成功")
            return True

        except Exception as e:
            print(f"❌ Hive连接失败: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """断开Hive连接"""
        if self.connection:
            try:
                self.connection.close()
                print("✅ Hive连接已断开")
            except Exception as e:
                print(f"⚠️ Hive断开连接时出错: {e}")
            finally:
                self.connection = None
                self.connected = False

    def execute_query(self, sql: str, task: DataTask) -> Dict[str, Any]:
        """执行SQL查询"""
        if not self.connected or not self.connection:
            return {
                'success': False,
                'error': 'Hive未连接',
                'data': None,
                'row_count': 0,
                'execution_time': 0
            }

        start_time = time.time()

        try:
            cursor = self.connection.cursor()

            # 执行查询
            cursor.execute(sql)

            # 获取结果
            result_data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            # 转换为字典格式
            data = []
            for row in result_data:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col] = row[i]
                data.append(row_dict)

            cursor.close()

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
            error_msg = f"Hive查询执行失败: {str(e)}"

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
        if not self.connected or not self.connection:
            return 0

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()
            cursor.close()

            return result[0] if result else 0
        except Exception as e:
            print(f"Hive计数查询失败: {e}")
            return 0

    def get_status(self) -> Dict[str, Any]:
        """获取Hive状态"""
        if not self.connection:
            return {'connected': False}

        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()

            return {
                'connected': True,
                'database': self.config.get('database', 'default')
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }

    def cancel_task(self, task_id: str):
        """取消任务（Hive中较难实现）"""
        print(f"⚠️ Hive任务取消功能有限: {task_id}")

    def list_databases(self) -> list:
        """列出所有数据库"""
        if not self.connection:
            return []

        try:
            cursor = self.connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return databases
        except Exception:
            return []

    def list_tables(self, database: Optional[str] = None) -> list:
        """列出数据库中的表"""
        if not self.connection:
            return []

        try:
            cursor = self.connection.cursor()

            if database:
                cursor.execute(f"USE {database}")

            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return tables
        except Exception:
            return []
