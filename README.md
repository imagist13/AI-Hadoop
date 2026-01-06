# BigData Agent - 离线大数据处理智能代理

基于AI的离线大数据处理智能代理系统，支持自然语言查询转换为SQL执行。

## 特性

- 🤖 **自然语言查询**: 支持中文自然语言查询大数据
- ⚡ **多引擎支持**: 支持Spark、Hive等多种执行引擎
- 📊 **智能分析**: 自动识别查询意图和数据模式
- 🎨 **多格式输出**: 支持JSON、CSV、图表等多种输出格式
- 🔧 **易于扩展**: 插件化架构，支持自定义组件

## 快速开始

### 环境要求

- Python 3.8+
- Java 8+ (用于Spark)
- Hadoop/Spark集群 (可选，本地模式支持单机测试)

### 安装依赖

```bash
pip install pyspark langchain openai
```

### 基本使用

```python
from bigdata_agent import BigDataAgent

# 初始化Agent
agent = BigDataAgent(engine_type="spark")

# 连接执行引擎
agent.connect()

# 执行自然语言查询
result = agent.query("统计昨天用户注册数")

# 处理结果
if result['success']:
    print(f"查询成功，返回 {result['metadata']['row_count']} 行数据")

# 断开连接
agent.disconnect()
```

### 命令行使用

```bash
# 基本查询
python -m bigdata_agent.web.cli "统计各省份用户数"

# 指定输出格式
python -m bigdata_agent.web.cli "分析销售额趋势" --format chart

# 预览查询结果
python -m bigdata_agent.web.cli "查询订单数据" --preview

# 估算查询成本
python -m bigdata_agent.web.cli "复杂分析查询" --estimate-cost
```

## 架构组件

```
bigdata_agent/
├── core/           # 核心组件
│   └── agent.py    # 主Agent类
├── nlp/            # 自然语言处理
│   ├── intent_recognizer.py    # 意图识别
│   └── query_analyzer.py       # 查询分析
├── task/           # 任务处理
│   ├── sql_generator.py        # SQL生成
│   └── task_builder.py         # 任务构建
├── execution/      # 执行引擎
│   ├── engine_factory.py       # 引擎工厂
│   ├── spark_engine.py         # Spark引擎
│   └── hive_engine.py          # Hive引擎
├── result/         # 结果处理
│   ├── result_processor.py     # 结果处理器
│   └── formatters.py          # 格式化器
└── web/            # 接口层
    └── cli.py      # 命令行接口
```

## 配置说明

创建 `setting.json` 配置文件：

```json
{
  "SILICONFLOW_API_KEY": "your-api-key",
  "SILICONFLOW_BASE_URL": "https://api.siliconflow.cn/v1",
  "SILICONFLOW_CHAT_MODEL": "deepseek-ai/DeepSeek-V3"
}
```

## 测试

运行测试套件：

```bash
python test_bigdata_agent.py
```

## 支持的查询类型

- **统计查询**: "统计用户总数"、"计算平均销售额"
- **分析查询**: "分析用户行为"、"趋势分析"
- **筛选查询**: "查找活跃用户"、"筛选高价值客户"
- **聚合查询**: "按省份分组统计"、"按月统计订单"

## 扩展开发

### 添加新的执行引擎

1. 继承 `ExecutionEngine` 基类
2. 实现所需的方法
3. 在 `EngineFactory` 中注册

### 添加新的输出格式

1. 继承 `ResultFormatter` 基类
2. 实现 `format` 方法
3. 在 `ResultProcessor` 中注册

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
