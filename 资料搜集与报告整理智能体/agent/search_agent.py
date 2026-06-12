"""
搜索智能体 —— 负责自动搜集互联网上的相关资料
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.web_search import WebSearchTool


class SearchAgent:
    """搜索智能体：根据用户主题自动搜集资料"""

    def __init__(self, search_provider: str = "duckduckgo", bing_api_key: str = None):
        """
        初始化搜索智能体

        Args:
            search_provider: 搜索引擎
            bing_api_key: Bing API 密钥
        """
        self.search_tool = WebSearchTool(provider=search_provider, bing_api_key=bing_api_key)

    def collect(self, topic: str, num_results: int = 8, depth: int = 2) -> dict:
        """
        根据主题搜集资料

        Args:
            topic: 研究主题
            num_results: 每次搜索返回结果数
            depth: 搜索深度（1=仅搜索主题，2=搜索主题及相关子主题）

        Returns:
            收集到的资料集合
        """
        print(f"\n  [SEARCH] 开始搜集资料，主题: {topic}")
        print(f"  [SEARCH] 搜索深度: {depth}, 每轮结果数: {num_results}")

        all_materials = {
            "topic": topic,
            "sources": [],
            "raw_contents": [],
        }

        # 第一轮：搜索主题
        search_queries = [topic]

        # 扩展搜索词
        if depth >= 2:
            extended_queries = [
                f"{topic} 最新进展",
                f"{topic} 应用案例",
                f"{topic} 发展趋势",
            ]
            search_queries.extend(extended_queries)

        # 执行搜索
        seen_urls = set()
        for query in search_queries:
            print(f"  [SEARCH] 搜索: {query}")
            results = self.search_tool.search(query, num_results=num_results)

            for item in results:
                url = item.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_materials["sources"].append({
                        "title": item.get("title", ""),
                        "url": url,
                        "snippet": item.get("snippet", ""),
                        "query": query,
                    })

        # 获取部分重要页面的详细内容
        print(f"  [PAGE] 获取详细内容...")
        max_pages = min(5, len(all_materials["sources"]))
        for i, source in enumerate(all_materials["sources"][:max_pages]):
            if source["url"]:
                print(f"  [PAGE] 读取: {source['title'][:40]}...")
                content = self.search_tool.fetch_page_content(source["url"], max_length=3000)
                if content:
                    all_materials["raw_contents"].append({
                        "url": source["url"],
                        "title": source["title"],
                        "content": content,
                    })

        print(f"  [OK] 资料搜集完成！共找到 {len(all_materials['sources'])} 个来源，"
              f"获取 {len(all_materials['raw_contents'])} 个页面详情")

        return all_materials

    def close(self):
        """释放资源"""
        self.search_tool.close()
