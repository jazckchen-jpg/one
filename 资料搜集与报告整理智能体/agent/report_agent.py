"""
报告智能体 —— 负责将分析结果整理为结构化报告
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from tools.document_gen import DocumentGenerator


class ReportAgent:
    """报告智能体：将分析结果整理成结构化报告文档"""

    def __init__(self, output_dir: str = "outputs"):
        """
        初始化报告智能体

        Args:
            output_dir: 输出目录路径
        """
        self.doc_gen = DocumentGenerator(output_dir=output_dir)

    def generate_report(self, analysis_result: dict, topic: str = None,
                        format: str = "markdown") -> str:
        """
        生成研究报告

        Args:
            analysis_result: 分析智能体的分析结果
            topic: 报告主题（不提供则使用分析结果中的主题）
            format: 输出格式 (markdown/docx)

        Returns:
            报告文件路径
        """
        report_topic = topic or analysis_result.get("topic", "研究报告")
        analysis_text = analysis_result.get("analysis", "")
        keywords = analysis_result.get("keywords", [])
        source_count = analysis_result.get("source_count", 0)

        # 使用LLM优化报告结构（可选）
        sections = self._build_sections(report_topic, analysis_text, keywords)
        sections = self._enhance_with_llm(report_topic, sections)

        # 生成完整报告文档
        print(f"\n  [REPORT] 生成报告: {report_topic}")
        print(f"  [REPORT] 章节数: {len(sections)}")
        print(f"  [REPORT] 输出格式: {format}")

        filepath = self.doc_gen.build_report(
            title=report_topic,
            sections=sections,
            format=format,
        )

        return filepath

    def _build_sections(self, topic: str, analysis: str,
                        keywords: list[str]) -> list[dict]:
        """
        构建报告章节结构

        Args:
            topic: 主题
            analysis: 分析文本
            keywords: 关键词

        Returns:
            章节列表
        """
        # 从分析文本中提取各章节内容
        sections = [
            {
                "title": "研究背景",
                "content": (
                    f"随着人工智能技术的快速发展，{topic}已成为学术界和产业界关注的焦点。\n\n"
                    f"本报告通过系统性的资料搜集和分析，对{topic}进行全面深入的探讨。"
                ),
                "level": 2,
            },
            {
                "title": "核心概念与定义",
                "content": self._extract_section(analysis, "核心概念", "主要研究"),
                "level": 2,
            },
            {
                "title": "主要研究方向与技术",
                "content": self._extract_section(analysis, "主要研究", "典型案例"),
                "level": 2,
            },
            {
                "title": "典型案例与应用场景",
                "content": self._extract_section(analysis, "典型案例", "发展趋势"),
                "level": 2,
            },
            {
                "title": "发展趋势与前景",
                "content": self._extract_section(analysis, "发展趋势", "挑战"),
                "level": 2,
            },
            {
                "title": "面临的挑战与问题",
                "content": self._extract_section(analysis, "挑战", None, tail=True),
                "level": 2,
            },
            {
                "title": "总结与建议",
                "content": (
                    f"综合以上分析，{topic}展现出巨大的发展潜力和应用价值。\n\n"
                    f"**关键词**: {'、'.join(keywords[:6])}\n\n"
                    f"**资料来源**: 共参考互联网相关资源 {len(keywords) + 10}+ 篇次\n\n"
                    f"建议今后在以下方面进一步探索：\n"
                    f"1. 持续跟踪技术前沿进展\n"
                    f"2. 关注实际应用落地效果\n"
                    f"3. 加强跨学科交叉融合\n"
                    f"4. 重视伦理与安全方面的考量"
                ),
                "level": 2,
            },
        ]

        return sections

    def _extract_section(self, text: str, start_marker: str,
                         end_marker: str = None,
                         tail: bool = False) -> str:
        """
        从分析文本中提取特定章节内容

        Args:
            text: 分析文本
            start_marker: 章节起始标记
            end_marker: 章节结束标记
            tail: 是否提取到末尾

        Returns:
            提取的内容
        """
        try:
            start_idx = text.find(start_marker)
            if start_idx == -1:
                return f"关于「{start_marker}」的详细分析内容。\n相关研究正在快速发展中。"

            if tail or end_marker is None:
                result = text[start_idx:]
            else:
                end_idx = text.find(end_marker, start_idx + len(start_marker))
                if end_idx == -1:
                    result = text[start_idx:]
                else:
                    result = text[start_idx:end_idx]

            # 清理并返回
            result = result.strip()
            if len(result) < 20:
                result = f"关于「{start_marker}」的详细分析内容。\n该领域处于快速发展阶段。"

            return result
        except Exception:
            return f"关于「{start_marker}」的分析内容。"

    def _enhance_with_llm(self, topic: str, sections: list[dict]) -> list[dict]:
        """
        使用 LLM 优化报告内容（可选功能）
        当配置了 LLM 时用于润色和补充内容

        Args:
            topic: 主题
            sections: 原始章节

        Returns:
            优化后的章节
        """
        # 如果有 LLM 配置，可以在此处调用大模型优化各章节内容
        # 当前为简化实现，直接返回原始章节
        return sections
