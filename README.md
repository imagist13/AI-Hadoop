# 🤖 BigData Agent - 离线大数据处理智能代理

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

基于AI的离线大数据处理智能代理系统，支持自然语言查询转换为SQL执行。通过集成硅基流动等LLM服务，将用户的自然语言查询智能转换为大数据SQL语句，并在Hadoop/Spark集群上执行。

## ✨ 特性

- 🧠 **自然语言查询**: 支持中文自然语言查询大数据
- ⚡ **多引擎支持**: 支持Spark、Hive等多种大数据处理引擎
- 📊 **智能SQL生成**: 自动生成高效的SQL查询语句
- 🎨 **多样化展示**: 支持图表、表格、JSON等多种输出格式
- 🛠️ **完整配置**: 支持JSON+YAML双重配置系统
- 📝 **丰富日志**: 内置完整的日志和监控系统
- 🔧 **插件架构**: 支持扩展新的数据源和处理引擎

## 特性

- 🤖 **自然语言查询**: 支持中文自然语言查询大数据
- ⚡ **多引擎支持**: 支持Spark、Hive等多种执行引擎
- 📊 **智能分析**: 自动识别查询意图和数据模式
- 🎨 **多格式输出**: 支持JSON、CSV、图表等多种输出格式
- 🔧 **易于扩展**: 插件化架构，支持自定义组件

## 🚀 快速开始

### 环境要求

- **Python**: 3.8+
- **Java**: 8+ (用于Spark)
- **大数据集群**: Hadoop/Spark (可选，支持本地模式测试)

### 📦 安装依赖

```bash
# 克隆项目
git clone https://github.com/your-username/bigdata-agent.git
cd bigdata-agent

# 安装Python依赖
pip install pyspark langchain openai pyyaml

# 或者使用requirements.txt（如果有的话）
pip install -r requirements.txt
```

### ⚙️ 配置设置

1. **复制配置文件**:
```bash
cp setting.json.example setting.json
cp config/cluster_config.yaml.example config/cluster_config.yaml
```

2. **编辑配置**:
- 在 `setting.json` 中设置硅基流动API密钥
- 在 `cluster_config.yaml` 中配置集群连接信息

### 💻 基本使用

#### Python API

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

#### 命令行使用

```bash
# 基本查询
python -m bigdata_agent.web.cli "统计各省份用户数"

# 指定输出格式
python -m bigdata_agent.web.cli "分析销售额趋势" --format chart

# 预览查询结果
python -m bigdata_agent.web.cli "查询订单数据" --preview
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

## 📁 项目结构

```
bigdata-agent/
├── bigdata_agent/              # 核心模块
│   ├── core/                   # 核心组件
│   │   ├── agent.py           # 主Agent类
│   │   └── base_llm.py       # LLM基类
│   ├── nlp/                   # 自然语言处理
│   │   ├── intent_recognizer.py    # 意图识别
│   │   └── query_analyzer.py       # 查询分析
│   ├── task/                  # 任务处理
│   │   ├── sql_generator.py        # SQL生成
│   │   └── task_builder.py         # 任务构建
│   ├── execution/             # 执行引擎
│   │   ├── engine_factory.py       # 引擎工厂
│   │   ├── spark_engine.py         # Spark引擎
│   │   └── hive_engine.py          # Hive引擎
│   ├── result/                # 结果处理
│   │   ├── result_processor.py     # 结果处理器
│   │   └── formatters.py           # 格式化器
│   └── web/                   # 接口层
│       └── cli.py             # 命令行接口
├── config/                    # 配置模块
│   ├── logging_config.py      # 日志配置
│   └── cluster_config.yaml    # 集群配置
├── llms/                      # LLM集成
│   ├── siliconflow_llm.py     # 硅基流动集成
│   └── settings_loader.py     # 配置加载
├── prompts/                   # AI提示词
│   ├── system_prompt.txt      # 系统级提示词
│   ├── query_analysis.txt     # 查询分析提示词
│   ├── sql_generation.txt     # SQL生成提示词
│   ├── intent_recognition.txt # 意图识别提示词
│   └── result_formatting.txt  # 结果格式化提示词
├── logs/                      # 日志文件（自动生成）
├── test/                      # 测试文件
├── bigdata_agent_design.md    # 设计文档
├── README.md                  # 项目文档
├── setting.json.example       # 配置示例
└── .gitignore                # Git忽略文件
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

## 🤝 贡献指南

我们欢迎各种形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细的贡献流程。

### 开发流程

1. Fork 本仓库
2. 创建特性分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 提交 Pull Request

### 代码规范

- 使用 `black` 格式化代码
- 添加必要的单元测试
- 更新相关文档
- 遵循现有的代码风格

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [硅基流动](https://siliconflow.cn/) - 提供强大的LLM服务
- [Apache Spark](https://spark.apache.org/) - 大数据处理框架
- [Apache Hive](https://hive.apache.org/) - 数据仓库工具

## 📞 联系方式

- 项目维护者: [您的GitHub用户名]
- 项目主页: https://github.com/your-username/bigdata-agent
- 问题反馈: [Issues](https://github.com/your-username/bigdata-agent/issues)

---

⭐ 如果这个项目对你有帮助，请给我们一个星标！

## 贡献

欢迎提交Issue和Pull Request！
