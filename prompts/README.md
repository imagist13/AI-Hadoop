# BigData Agent 提示词文档

这个目录包含了BigData Agent系统中使用的各种AI提示词文件，用于指导AI模型的行为和响应。

## 文件结构

```
prompts/
├── system_prompt.txt      # 系统级提示词 - 定义整体行为准则
├── query_analysis.txt     # 查询分析提示词 - NLP理解用户查询
├── sql_generation.txt     # SQL生成提示词 - 将查询转换为SQL语句
├── intent_recognition.txt # 意图识别提示词 - 识别查询意图类型
├── result_formatting.txt  # 结果格式化提示词 - 数据展示和可视化
└── README.md             # 本文档
```

## 提示词使用指南

### 1. 系统级提示词 (system_prompt.txt)
**用途**: 定义Agent的整体角色、能力和行为准则
**使用场景**: 初始化AI助手时的系统消息
**重要性**: ⭐⭐⭐⭐⭐ (最高优先级)

### 2. 查询分析提示词 (query_analysis.txt)
**用途**: 指导AI理解和解析用户的自然语言查询
**使用场景**: NLP处理模块
**输出格式**: 结构化JSON
**重要性**: ⭐⭐⭐⭐⭐

### 3. SQL生成提示词 (sql_generation.txt)
**用途**: 将解析后的查询转换为具体的SQL语句
**使用场景**: 任务构建模块
**支持方言**: Hive, Spark SQL, Presto
**重要性**: ⭐⭐⭐⭐⭐

### 4. 意图识别提示词 (intent_recognition.txt)
**用途**: 识别用户查询的具体意图类型
**支持意图**: 统计、分析、趋势、对比、筛选等9种类型
**输出格式**: 结构化JSON with 置信度
**重要性**: ⭐⭐⭐⭐⭐

### 5. 结果格式化提示词 (result_formatting.txt)
**用途**: 将查询结果转换为用户友好的展示格式
**支持格式**: 表格、图表、JSON、统计摘要
**可视化**: 支持多种图表类型
**重要性**: ⭐⭐⭐⭐

## 提示词编写原则

### 1. 清晰明确
- 使用简单明了的语言
- 避免歧义和模糊表达
- 提供具体的示例

### 2. 结构化组织
- 按照功能模块组织内容
- 使用标题和列表增强可读性
- 提供清晰的层次结构

### 3. 完整性覆盖
- 覆盖主要使用场景
- 提供异常情况处理
- 包含边界条件说明

### 4. 一致性维护
- 术语使用保持一致
- 输出格式标准化
- 行为准则统一

## 自定义和扩展

### 添加新的提示词
1. 在相应目录创建新的`.txt`文件
2. 遵循现有的命名和格式规范
3. 在代码中引用新的提示词文件

### 修改现有提示词
1. 备份原有文件
2. 修改内容时保持向后兼容
3. 更新相关文档和示例
4. 测试修改效果

## 最佳实践

### 1. 版本控制
- 所有提示词文件纳入版本控制
- 记录修改历史和原因
- 支持回滚到之前的版本

### 2. 测试验证
- 为每个提示词创建测试用例
- 验证输出格式的正确性
- 确保在各种场景下都能正常工作

### 3. 性能监控
- 监控提示词的效果和准确性
- 收集用户反馈进行改进
- 定期review和优化

### 4. 安全性考虑
- 避免在提示词中包含敏感信息
- 确保不会生成有害或不安全的响应
- 实施适当的输入验证

## 使用示例

### 在Python代码中使用
```python
def load_prompt(file_name: str) -> str:
    """加载提示词文件"""
    prompt_path = Path(__file__).parent / file_name
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

# 使用系统提示词
system_prompt = load_prompt('system_prompt.txt')

# 使用查询分析提示词
analysis_prompt = load_prompt('query_analysis.txt')
```

### 集成到AI模型调用
```python
def analyze_query(user_query: str) -> dict:
    """分析用户查询"""
    analysis_prompt = load_prompt('query_analysis.txt')

    full_prompt = f"{analysis_prompt}\n\n用户查询：{user_query}"

    # 调用AI模型
    response = ai_model.generate(full_prompt)

    # 解析JSON响应
    return json.loads(response)
```

## 维护建议

### 定期review
- 每季度review一次提示词的有效性
- 根据用户反馈进行调整
- 跟进行业最佳实践的更新

### 性能优化
- 优化提示词长度，减少token消耗
- 提高响应准确性和相关性
- 平衡响应速度和质量

### 扩展性设计
- 为新功能预留扩展空间
- 支持模块化组合使用
- 保持向后兼容性

## 常见问题

### Q: 提示词文件太大怎么办？
A: 将大的提示词拆分为多个专用文件，按功能模块组织。

### Q: 如何处理多语言支持？
A: 为不同语言创建对应的提示词文件，使用统一的命名规范。

### Q: 提示词效果不佳怎么办？
A: 检查提示词的清晰度和具体性，添加更多示例和约束条件。

---

*如有问题或建议，请联系BigData Agent开发团队。*
