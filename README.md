# CV-Refiner 简历评估与优化

基于 GPT-4o 的智能简历评估与优化工具，提供 Web 对话界面，支持：

- **目标职位定制化评估** — 输入 JD，评估与优化建议针对具体岗位要求
- **五/六维度评估** — 结构完整性、语言表达、关键词覆盖、量化成果、冗余内容 + 岗位匹配度
- **优化简历生成** — 评估后直接输出一份可用的优化简历草稿
- **对话式追问** — 对评估结果逐条讨论、修改、对比前后差异
- **文件上传** — 支持 PDF / DOCX / TXT 格式简历自动提取文本

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入你的 OpenAI API Key
```

### 3. 启动应用

```bash
python app.py
```

访问 `http://localhost:7860` 使用 Web 界面。

## 使用方法

### 简历评估（Tab 1）

1. **上传简历**：支持 PDF、DOCX、TXT 文件，或直接粘贴简历文本
2. **输入目标职位描述**（推荐）：粘贴目标岗位 JD，将启用"岗位匹配度"评估维度
3. **点击"开始评估"**：生成评估报告 + 优化简历草稿 + 前后对比

### 对话追问（Tab 2）

完成评估后切换到对话标签，可以：
- 针对具体问题追问修改建议
- 要求重写某段经历
- 对比修改前后差异
- 讨论优化策略

## 项目结构

```
CV-Refiner/
├── app.py                  # Gradio Web 应用入口
├── cv_engine.py            # 核心逻辑：评估、优化、对话、diff
├── document_parser.py      # PDF/DOCX/TXT 文本提取
├── prompts.py              # LLM Prompt 模板
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板
├── cv_refiner_workflow.yml # Dify 工作流定义（参考）
└── examples/
    └── sample_resume.txt   # 测试用示例简历
```

## 评估维度

| 维度 | 评估内容 |
|------|----------|
| 结构完整性 | 核心模块是否齐全（个人信息、教育、经历、技能等） |
| 语言表达 | 用词是否专业简洁、语法正确、动词有力 |
| 关键词覆盖 | 行业术语、技术栈是否充分体现 |
| 量化成果 | 工作成果是否有数据支撑 |
| 冗余内容 | 是否存在无关信息、重复表述 |
| 岗位匹配度 | （提供 JD 时）技能与经历是否匹配岗位要求 |

## 自定义

- **切换模型**：修改 `cv_engine.py` 中的 `model` 参数
- **调整评估标准**：编辑 `prompts.py` 中的 prompt 模板
- **调整温度**：修改 `cv_engine.py` 中 `temperature` 值

## Dify 工作流（参考）

项目同时保留了原始的 Dify 平台工作流定义 `cv_refiner_workflow.yml`，可导入 Dify 平台使用基础评估功能。详见文件内注释。

## License

MIT
