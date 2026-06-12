#!/usr/bin/env python3
"""
基于大模型的资料搜集与报告整理智能体 —— 主程序入口

用法:
    python main.py --topic "人工智能在医疗领域的应用"
    python main.py --topic "量子计算最新进展" --format docx
    python main.py --topic "碳中和与新能源技术" --search bing --depth 2

中科大 2025-2026学年 《人工智能基础与实践》 课程设计
"""

import argparse
import sys
import os

# 设置控制台编码为 UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 确保可以导入工具和智能体模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="基于大模型的资料搜集与报告整理智能体",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --topic "人工智能在医疗领域的应用"
  python main.py --topic "深度学习最新进展" --format docx --depth 2
  python main.py --topic "量子计算" --search duckduckgo
        """,
    )
    parser.add_argument(
        "--topic", "-t",
        type=str,
        required=True,
        help="研究主题（例如：人工智能在医疗领域的应用）",
    )
    parser.add_argument(
        "--format", "-f",
        type=str,
        default="markdown",
        choices=["markdown", "docx"],
        help="输出报告格式 (默认: markdown)",
    )
    parser.add_argument(
        "--search", "-s",
        type=str,
        default=None,
        choices=["duckduckgo", "bing"],
        help="搜索引擎 (默认使用 config.py 中的配置)",
    )
    parser.add_argument(
        "--depth", "-d",
        type=int,
        default=2,
        choices=[1, 2],
        help="搜索深度: 1=仅搜索主主题, 2=搜索扩展子主题 (默认: 2)",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="outputs",
        help="报告输出目录 (默认: outputs)",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        choices=["mock", "dashscope", "qianfan", "openai-compat"],
        help="大模型供应商 (默认使用 config.py 中的配置)",
    )
    return parser.parse_args()


def print_banner():
    """打印启动横幅"""
    banner = """
+====================================================+
|       资料搜集与报告整理智能体                       |
|    基于大模型的信息检索与报告自动生成系统            |
|   《人工智能基础与实践》课程设计                    |
+====================================================+
    """
    print(banner)


def print_summary(topic, search_results, analysis, report_path):
    """打印执行摘要"""
    print("\n" + "=" * 60)
    print("  执行摘要")
    print("=" * 60)
    print(f"  主题:      {topic}")
    print(f"  信息来源:  {search_results} 条")
    print(f"  关键词:    {', '.join(analysis.get('keywords', []))}")
    print(f"  报告路径:  {report_path}")
    print("=" * 60 + "\n")


def main():
    """主函数"""
    args = parse_args()

    # 打印横幅
    print_banner()

    # 导入配置
    try:
        import config
    except ImportError:
        print("  [!] 未找到 config.py，使用默认配置")
        config = None

    # 配置参数
    search_provider = args.search or (
        getattr(config, "SEARCH_PROVIDER", "duckduckgo") if config else "duckduckgo"
    )
    bing_api_key = getattr(config, "BING_API_KEY", "") if config else ""
    llm_provider = args.provider or (
        getattr(config, "LLM_PROVIDER", "mock") if config else "mock"
    )

    # 获取 API 密钥
    api_key = ""
    model = ""
    if config:
        if llm_provider == "dashscope":
            api_key = getattr(config, "DASHSCOPE_API_KEY", "")
            model = getattr(config, "DASHSCOPE_MODEL", "qwen-turbo")
        elif llm_provider == "qianfan":
            api_key = getattr(config, "QIANFAN_API_KEY", "")
            model = getattr(config, "QIANFAN_MODEL", "")

    # ========== 阶段一：资料搜集 ==========
    print("\n" + "─" * 50)
    print("  阶段一/三：资料搜集")
    print("─" * 50)

    from agent.search_agent import SearchAgent
    search_agent = SearchAgent(
        search_provider=search_provider,
        bing_api_key=bing_api_key,
    )

    try:
        materials = search_agent.collect(
            topic=args.topic,
            num_results=8,
            depth=args.depth,
        )
    finally:
        search_agent.close()

    if not materials["sources"]:
        print("\n  [!] 未搜索到相关结果，尝试使用模拟数据完成演示...\n")
        # 使用模拟数据
        materials["sources"] = [
            {"title": f"{args.topic} - 学术研究", "url": "", "snippet": f"{args.topic}的学术研究进展"},
            {"title": f"{args.topic} - 应用实践", "url": "", "snippet": f"{args.topic}在实际场景中的应用"},
            {"title": f"{args.topic} - 发展趋势", "url": "", "snippet": f"{args.topic}的未来发展趋势"},
        ]

    # ========== 阶段二：智能分析 ==========
    print("\n" + "─" * 50)
    print("  阶段二/三：智能分析")
    print("─" * 50)

    from agent.analysis_agent import AnalysisAgent
    analysis_agent = AnalysisAgent(
        provider=llm_provider,
        api_key=api_key,
        model=model,
    )

    try:
        analysis_result = analysis_agent.analyze_materials(materials)
    finally:
        analysis_agent.close()

    # ========== 阶段三：报告生成 ==========
    print("\n" + "─" * 50)
    print("  阶段三/三：报告生成")
    print("─" * 50)

    from agent.report_agent import ReportAgent
    report_agent = ReportAgent(output_dir=args.output)

    report_path = report_agent.generate_report(
        analysis_result=analysis_result,
        topic=args.topic,
        format=args.format,
    )

    # ========== 打印摘要 ==========
    print_summary(args.topic, len(materials["sources"]), analysis_result, report_path)

    print("  [OK] 全部流程完成！")
    print(f"  [OK] 报告文件: {os.path.abspath(report_path)}")
    print()


if __name__ == "__main__":
    main()
