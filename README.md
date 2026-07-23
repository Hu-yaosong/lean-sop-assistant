# 精益 SOP 智能助手 🏭

基于 RAG（检索增强生成）技术的精益文档智能问答系统。上传你的精益生产文档，即可用自然语言提问。

## 📋 功能

- 解析 PDF、PPTX、DOCX、XLSX、TXT 等格式的精益文档
- 自动构建向量知识库（本地存储，数据不出电脑）
- 基于 DeepSeek API 的智能问答
- 每一条回答都标注引用来源

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 获取 API Key

1. 打开 [platform.deepseek.com](https://platform.deepseek.com) 注册账号
2. 进入「API Keys」页面创建新的 API Key
3. 充值少量余额（约 10-20 元够用很久）

### 3. 构建知识库

```bash
cd 精益SOP助手
python build_knowledge_base.py
```

> ⚠️ 首次使用前，请修改 `build_knowledge_base.py` 中的 `DOCUMENTS_DIR` 路径，指向你的精益文档文件夹。

### 4. 启动问答助手

```bash
python -m streamlit run sop_assistant.py
```

浏览器会自动打开 http://localhost:8501

### 一键启动（Windows）

双击「精益SOP助手.exe」即可自动启动服务并打开浏览器。
（如果尚未构建知识库，启动器会自动运行构建脚本。）

## 💬 使用示例

在侧边栏输入 DeepSeek API Key 后，可以问：

- 「七大浪费有哪些？怎么消除？」
- 「如何绘制价值流程图？」
- 「5S 的实施步骤是什么？」
- 「生产线平衡率如何计算？」
- 「有没有改善案例可以参考？」
- 「什么是拉动式生产？」

## 📁 项目结构

```
精益SOP助手/
├── build_knowledge_base.py   # 知识库构建脚本
├── sop_assistant.py          # Streamlit 问答应用
├── requirements.txt          # Python 依赖
├── README.md                 # 本文件
├── knowledge_base/           # 知识库文件（自动生成）
│   ├── chunks.pkl            #   文本块
│   ├── vectorizer.pkl        #   TF-IDF 向量化器
│   ├── tfidf_matrix.pkl      #   TF-IDF 矩阵
│   └── sources.txt           #   来源文件列表
├── 操作指南.png              # 使用截图
├── 精益SOP助手.exe           # Windows 一键启动器
└── 启动精益助手.bat          # 批处理启动器
```

## 📊 成本估计

| 项目 | 费用 |
|------|------|
| DeepSeek API 充值 | 10-20 元（够用几个月） |
| 数据存储 | 全部本地，免费 |
| 服务器 | 本地运行，不需要云服务 |

## ⚙️ 架构说明

```
用户提问
   │
   ▼
[TF-IDF 向量检索 ← 本地知识库]
   │ 检索 Top-5 相关文档片段
   ▼
[构建 Prompt（上下文 + 问题）]
   │
   ▼
[DeepSeek Chat API → 生成回答]
   │
   ▼
[展示回答 + 引用来源]
```
