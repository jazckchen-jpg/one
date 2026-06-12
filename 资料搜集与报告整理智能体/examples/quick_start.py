#!/usr/bin/env python3
"""
快速启动脚本 —— 一键运行
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    # 在命令行运行: python quick_start.py
    topic = "人工智能在医疗领域的应用"

    print(f"开始研究: {topic}")
    print("=" * 50)

    from agent.search_agent import SearchAgent
    from agent.analysis_agent import AnalysisAgent
    from agent.report_agent import ReportAgent

    # 1. 搜集资料
    print("\n阶段1: 搜集资料...")
    searcher = SearchAgent()
    materials = searcher.collect(topic)

    # 2. 分析资料
    print("\n阶段2: 分析资料...")
    analyzer = AnalysisAgent(provider="mock")
    result = analyzer.analyze_materials(materials)

    # 3. 生成报告
    print("\n阶段3: 生成报告...")
    reporter = ReportAgent(output_dir="outputs")
    path = reporter.generate_report(result, topic=topic)

    searcher.close()

    print(f"\n✅ 完成！报告路径: {path}")
