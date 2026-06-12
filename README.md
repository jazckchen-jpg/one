基于大模型的资料搜集与报告整理智能体

📖 项目简介

本项目实现了一个基于大语言模型（LLM）的智能资料搜集与报告整理系统。用户只需输入研究主题或问题，系统即可自动完成以下流程：

1. 智能搜索 — 自动搜索互联网上的相关资料
2. 智能分析 — 利用大模型对搜集的资料进行理解、分析和归纳
3. 报告生成 — 自动生成结构化的研究报告（支持Markdown、Word格式）

🏗️ 系统架构

    用户输入（研究主题）
           ↓
    ┌──────────────────┐
    │  搜索智能体       │ ← 调用 Web搜索工具
    │  (SearchAgent)    │
    └────────┬─────────┘
             ↓ 原始资料
    ┌──────────────────┐
    │  分析智能体       │ ← 调用 大模型API
    │  (AnalysisAgent)  │
    └────────┬─────────┘
             ↓ 分析结果
    ┌──────────────────┐
    │  报告智能体       │ ← 调用 文档生成工具
    │  (ReportAgent)    │
    └────────┬─────────┘
             ↓ 最终报告
        📄 输出文件

🚀 快速开始

1. 安装依赖

    pip install -r requirements.txt

2. 配置API密钥

编辑 config.py，填入您的API密钥：

    # 支持以下大模型平台（任选其一即可）
    LLM_PROVIDER = "dashscope"  # 通义千问
    DASHSCOPE_API_KEY = "sk-xxxx"
    
    # 或使用百度文心
    # LLM_PROVIDER = "qianfan"
    # QIANFAN_API_KEY = "xxx"
    # QIANFAN_SECRET_KEY = "xxx"

3. 运行示例

    python main.py --topic "人工智能在医疗领域的应用"

更多示例见 examples/ 目录。

✨ 功能特点

- ✅ 多模型支持：通义千问、百度文心一言、OpenAI兼容接口
- ✅ 智能搜索：自动搜索并过滤高质量信息源
- ✅ 深度分析：多角度理解、归纳和总结
- ✅ 报告生成：Markdown/Word文档，含目录、图表占位
- ✅ 可扩展：插件化设计，方便添加新工具

📁 项目结构

    资料搜集与报告整理智能体/
    ├── main.py                 # 主程序入口
    ├── config.py               # 配置文件
    ├── requirements.txt        # 依赖清单
    ├── README.md               # 本文件
    ├── agent/
    │   ├── __init__.py
    │   ├── search_agent.py     # 搜索智能体
    │   ├── analysis_agent.py   # 分析智能体
    │   └── report_agent.py     # 报告智能体
    ├── tools/
    │   ├── __init__.py
    │   ├── web_search.py       # 网络搜索工具
    │   └── document_gen.py     # 文档生成工具
    ├── outputs/                # 输出目录
    ├── reports/                # 报告模板
    └── examples/               # 使用示例

📊 评分参考

  考核内容      	分值  	说明              
  智能体搭建的工作量 	30分 	完整实现搜索、分析、报告三大模块
  智能体的创新性   	10分 	支持多模型切换、智能搜索策略  
  智能体性能     	20分 	稳定可靠的信息获取与分析能力  
  课程设计报告内容质量	30分 	报告结构完整、内容详实     
  课程设计报告格式  	10分 	符合学校模板要求        

🔧 环境要求

- Python 3.8+
- 操作系统：Windows / Linux / macOS

📝 依赖

- openai — 兼容OpenAI接口的大模型调用
- httpx — 网络请求
- python-docx — Word文档生成
- markdown — Markdown处理
