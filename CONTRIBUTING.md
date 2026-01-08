# 🤝 贡献指南

感谢您对 BigData Agent 项目的兴趣！我们欢迎各种形式的贡献，包括但不限于：

- 🐛 报告bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- 🎨 改进UI/UX
- 📊 添加测试用例

## 📋 贡献流程

### 1. 准备工作

在开始贡献之前，请确保：

1. **阅读项目文档**: 熟悉项目的架构和设计理念
2. **设置开发环境**: 按照 README.md 中的说明配置环境
3. **运行测试**: 确保所有测试都能通过

```bash
# 运行测试
python test_comprehensive.py
```

### 2. 报告问题

如果您发现bug或有功能建议，请：

1. **检查现有Issues**: 确保问题没有被重复报告
2. **创建新Issue**: 使用清晰的标题和详细描述
3. **提供必要信息**:
   - 错误信息和堆栈跟踪
   - 复现步骤
   - 环境信息（Python版本、操作系统等）
   - 预期行为 vs 实际行为

### 3. 代码贡献

#### Fork 和 Clone

```bash
# Fork 项目到您的GitHub账户
# 然后克隆到本地
git clone https://github.com/your-username/bigdata-agent.git
cd bigdata-agent

# 添加上游仓库
git remote add upstream https://github.com/original-author/bigdata-agent.git
```

#### 创建特性分支

```bash
# 从main分支创建新分支
git checkout -b feature/your-feature-name

# 或者修复bug
git checkout -b fix/issue-number-description
```

#### 代码开发

1. **遵循代码规范**:
   ```bash
   # 使用black格式化代码
   pip install black
   black bigdata_agent/

   # 检查代码风格
   pip install flake8
   flake8 bigdata_agent/
   ```

2. **编写测试**:
   ```python
   # 为新功能添加测试
   def test_your_new_feature():
       # 测试代码
       pass
   ```

3. **更新文档**:
   - 修改相关的README内容
   - 添加代码注释
   - 更新类型提示

#### 提交代码

```bash
# 添加更改的文件
git add .

# 提交更改（使用清晰的提交信息）
git commit -m "feat: 添加新功能

- 添加了XXX功能
- 修复了XXX问题
- 更新了XXX文档

Closes #123"

# 推送到您的fork
git push origin feature/your-feature-name
```

#### 创建 Pull Request

1. 访问您的GitHub仓库
2. 点击 "Compare & pull request"
3. 填写PR描述：
   - 清晰描述更改内容
   - 关联相关Issue
   - 说明测试方法
4. 等待审核和合并

## 🎯 开发规范

### 代码风格

- 使用 `black` 自动格式化代码
- 遵循 PEP 8 规范
- 使用类型提示
- 添加必要的文档字符串

### 提交规范

使用 [Conventional Commits](https://conventionalcommits.org/) 格式：

```
type(scope): description

[optional body]

[optional footer]
```

**类型**:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建工具或辅助工具更新

**示例**:
```
feat(nlp): 添加意图识别功能

- 实现基于关键词的意图识别算法
- 支持统计、分析、筛选等多种意图类型
- 添加相应的测试用例

Closes #42
```

### 测试要求

- 新功能必须包含单元测试
- 修改现有功能时需要更新相关测试
- 所有测试必须通过
- 保持测试覆盖率在80%以上

### 文档要求

- 为所有公共函数添加docstring
- 更新相关的README和文档
- 为复杂逻辑添加代码注释
- 保持示例代码的时效性

## 🔧 开发环境设置

### 必需依赖

```bash
pip install -r requirements.txt
```

### 开发依赖

```bash
pip install -r requirements-dev.txt
```

### 运行测试

```bash
# 运行所有测试
python test_comprehensive.py

# 运行特定测试
python -m pytest test/test_specific.py -v

# 运行覆盖率测试
python -m pytest --cov=bigdata_agent --cov-report=html
```

## 🚨 行为准则

### 我们的承诺

我们致力于为所有人提供一个无骚扰的贡献环境，无论年龄、体型、残疾、民族、性别认同和表达、经验水平、国籍、外貌、种族、宗教或性取向如何。

### 标准

有助于创造积极环境的行为包括：

- 使用欢迎和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

不可接受的行为包括：

- 使用性暗示的语言或图像
- 进行人身攻击
- 发表辱骂性或侮辱性评论
- 公开或私下骚扰
- 发布他人的私人信息，如物理或电子地址
- 其他有理由认为不适当的行为

## 📞 联系方式

如果您有任何问题或需要帮助：

- 📧 发送邮件至项目维护者
- 💬 在GitHub Issues中提问
- 🐛 报告安全问题请发送邮件至安全团队

感谢您的贡献！🎉
