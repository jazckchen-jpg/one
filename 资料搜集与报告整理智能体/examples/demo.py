#!/usr/bin/env python3
"""
演示示例 —— 展示智能体的多种使用场景
运行方式: python -m examples.demo
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def demo_basic():
    """基础演示：简单主题搜索与报告生成"""
    print("\n" + "=" * 60)
    print("  示例1: 基础使用 - 简单主题搜索")
    print("=" * 60)

    from agent.search_agent import SearchAgent
    from agent.analysis_agent import AnalysisAgent
    from agent.report_agent import ReportAgent

    # 使用 mock 模式（无需 API 密钥）
    search_agent = SearchAgent()
    materials = search_agent.collect("人工智能", num_results=5, depth=1)

    analysis_agent = AnalysisAgent(provider="mock")
    result = analysis_agent.analyze_materials(materials)

    report_agent = ReportAgent(output_dir="outputs")
    path = report_agent.generate_report(result, topic="人工智能综述", format="markdown")

    print(f"\n  报告已生成: {path}")
    search_agent.close()


def demo_with_config():
    """使用配置文件的演示"""
    print("\n" + "=" * 60)
    print("  示例2: 使用配置文件")
    print("=" * 60)

    try:
        import config
        print(f"  当前配置: LLM提供商={config.LLM_PROVIDER}")
        print(f"  搜索引擎={config.SEARCH_PROVIDER}")
    except ImportError:
        print("  [!] 未找到 config.py")


def demo_report_formats():
    """演示不同报告格式"""
    print("\n" + "=" * 60)
    print("  示例3: 不同报告格式")
    print("=" * 60)

    from tools.document_gen import DocumentGenerator

    gen = DocumentGenerator(output_dir="outputs")

    sections = [
        {"title": "章节一", "content": "演示内容...", "level": 2},
        {"title": "章节二", "content": "更多内容...", "level": 2},
    ]

    md_path = gen.build_report("演示报告", sections, format="markdown")
    print(f"  Markdown: {md_path}")


if __name__ == "__main__":
print("资料搜集与报告整理智能体 - 演示示例")
    print("=" * 60)

    demo_basic()
    demo_with_config()
    demo_report_formats()

    print("\n✅ 演示完成！")
