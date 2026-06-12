"""
Web 搜索工具 —— 支持必应(网页)、百度、DuckDuckGo、Bing API 等多种搜索引擎
国内推荐使用: bing_html (必应网页搜索) 或 baidu (百度搜索)
"""

import json
import time
import re
from typing import Optional
from urllib.parse import quote_plus, urlparse, parse_qs

import httpx
from bs4 import BeautifulSoup


class WebSearchTool:
    """网络搜索工具，用于搜集互联网资料"""

    def __init__(self, provider: str = "bing_html", bing_api_key: Optional[str] = None):
        """
        初始化搜索工具

        Args:
            provider: 搜索引擎
                "bing_html"  - 必应网页搜索（推荐，国内可用，无需API Key）
                "baidu"      - 百度搜索（国内可用，无需API Key）
                "duckduckgo" - DuckDuckGo（国内可能超时）
                "bing"       - 必应API（需要API Key）
            bing_api_key: 必应搜索API密钥（仅 provider="bing" 时需要）
        """
        self.provider = provider
        self.bing_api_key = bing_api_key
        self._client = httpx.Client(timeout=10.0, follow_redirects=True, verify=False)
        self._user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )

    def search(self, query: str, num_results: int = 8) -> list[dict]:
        """
        执行搜索

        Args:
            query: 搜索关键词
            num_results: 返回结果数量

        Returns:
            搜索结果列表，每项包含 title, url, snippet
        """
        if self.provider == "bing_html":
            return self._search_bing_html(query, num_results)
        elif self.provider == "baidu":
            return self._search_baidu(query, num_results)
        elif self.provider == "duckduckgo":
            return self._search_duckduckgo(query, num_results)
        elif self.provider == "bing":
            return self._search_bing_api(query, num_results)
        else:
            raise ValueError(f"不支持的搜索源: {self.provider}")

    # ==================== 必应网页搜索（推荐） ====================

    def _search_bing_html(self, query: str, num_results: int) -> list[dict]:
        """
        使用必应网页搜索（无需API Key，国内可访问）
        """
        results = []
        url = f"https://cn.bing.com/search?q={quote_plus(query)}&count={num_results}"

        try:
            resp = self._client.get(url, headers={
                "User-Agent": self._user_agent,
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            })
            resp.encoding = "utf-8"

            soup = BeautifulSoup(resp.text, "html.parser")

            # 必应搜索结果在 <li class="b_algo"> 中
            for item in soup.select(".b_algo")[:num_results]:
                title_el = item.select_one("h2 a")
                snippet_el = item.select_one(".b_caption p, .b_lineclamp2")

                if title_el:
                    title = title_el.get_text(strip=True)
                    href = title_el.get("href", "")

                    snippet = snippet_el.get_text(strip=True) if snippet_el else ""

                    if href and not href.startswith("http"):
                        continue

                    results.append({
                        "title": title,
                        "url": href,
                        "snippet": snippet,
                    })

            # 如果没找到结果，试试备选选择器
            if not results:
                for item in soup.select("#b_results > li")[:num_results]:
                    title_el = item.select_one("h2 a")
                    if title_el:
                        title = title_el.get_text(strip=True)
                        href = title_el.get("href", "")
                        snippet_el = item.select_one(".b_caption p")
                        snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                        if href and href.startswith("http"):
                            results.append({
                                "title": title,
                                "url": href,
                                "snippet": snippet,
                            })

            if results:
                print(f"  [BING] 必应搜索成功，找到 {len(results)} 条结果")

        except Exception as e:
            print(f"  [!] 必应搜索出错: {e}")

        return results[:num_results]

    # ==================== 百度搜索 ====================

    def _search_baidu(self, query: str, num_results: int) -> list[dict]:
        """
        使用百度搜索（国内可访问，无需API Key）
        """
        results = []
        url = f"https://www.baidu.com/s?wd={quote_plus(query)}&rn={num_results}"

        try:
            resp = self._client.get(url, headers={
                "User-Agent": self._user_agent,
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Referer": "https://www.baidu.com/",
            })
            resp.encoding = "utf-8"

            soup = BeautifulSoup(resp.text, "html.parser")

            # 百度搜索结果在 .result 或 .c-container 中
            for item in soup.select(".result, .c-container")[:num_results]:
                title_el = item.select_one("h3 a, .t a")
                snippet_el = item.select_one(".c-abstract, .c-span-last, .content-right_8Zs40")

                if title_el:
                    title = title_el.get_text(strip=True)
                    href = title_el.get("href", "")

                    # 百度使用跳转链接，需要获取真实URL
                    if href.startswith("http"):
                        snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                        results.append({
                            "title": title,
                            "url": href,
                            "snippet": snippet,
                        })

            # 如果没有 result 类，尝试另一种选择器
            if not results:
                for item in soup.select("#content_left > div")[:num_results]:
                    title_el = item.select_one("h3 a")
                    if title_el:
                        title = title_el.get_text(strip=True)
                        href = title_el.get("href", "")
                        snippet_el = item.select_one(".c-abstract")
                        snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                        if href:
                            results.append({
                                "title": title,
                                "url": href,
                                "snippet": snippet,
                            })

            if results:
                print(f"  [BAIDU] 百度搜索成功，找到 {len(results)} 条结果")

        except Exception as e:
            print(f"  [!] 百度搜索出错: {e}")

        return results[:num_results]

    # ==================== DuckDuckGo ====================

    def _search_duckduckgo(self, query: str, num_results: int) -> list[dict]:
        """使用 DuckDuckGo 搜索（国内可能超时）"""
        results = []
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

        try:
            resp = self._client.get(url, headers={"User-Agent": self._user_agent})
            resp.encoding = "utf-8"

            soup = BeautifulSoup(resp.text, "html.parser")
            for item in soup.select(".result")[:num_results]:
                title_el = item.select_one(".result__title a")
                snippet_el = item.select_one(".result__snippet")

                if title_el:
                    title = title_el.get_text(strip=True)
                    href = title_el.get("href", "")
                    if "uddg=" in str(href):
                        parsed = urlparse(str(href))
                        qs = parse_qs(parsed.query)
                        href = qs.get("uddg", [""])[0]

                    snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                    results.append({
                        "title": title,
                        "url": href,
                        "snippet": snippet,
                    })

            if not results:
                results = self._search_duckduckgo_api(query, num_results)

        except Exception as e:
            print(f"  [!] DuckDuckGo 搜索出错: {e}")
            results = self._search_duckduckgo_api(query, num_results)

        return results

    def _search_duckduckgo_api(self, query: str, num_results: int) -> list[dict]:
        """DuckDuckGo API 备用方案"""
        results = []
        try:
            url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json"
            resp = self._client.get(url, headers={"User-Agent": self._user_agent})
            data = resp.json()

            if data.get("AbstractText"):
                results.append({
                    "title": data.get("AbstractTitle", ""),
                    "url": data.get("AbstractURL", ""),
                    "snippet": data.get("AbstractText", ""),
                })

            for topic in data.get("RelatedTopics", [])[:num_results - 1]:
                if "Text" in topic:
                    title = topic.get("Text", "").split(" - ")[0] if " - " in topic.get("Text", "") else topic.get("Text", "")
                    results.append({
                        "title": title,
                        "url": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", ""),
                    })
                elif "Topics" in topic:
                    for sub in topic["Topics"][:3]:
                        title = sub.get("Text", "").split(" - ")[0] if " - " in sub.get("Text", "") else sub.get("Text", "")
                        results.append({
                            "title": title,
                            "url": sub.get("FirstURL", ""),
                            "snippet": sub.get("Text", ""),
                        })
        except Exception as e:
            print(f"  [!] DuckDuckGo API 搜索出错: {e}")

        return results[:num_results]

    # ==================== 必应 API 搜索 ====================

    def _search_bing_api(self, query: str, num_results: int) -> list[dict]:
        """使用必应搜索 API（需要 API Key）"""
        if not self.bing_api_key:
            print("  [!] 未配置 Bing API 密钥，请设置 BING_API_KEY")
            return []

        results = []
        try:
            headers = {"Ocp-Apim-Subscription-Key": self.bing_api_key}
            params = {"q": query, "count": num_results, "mkt": "zh-CN"}
            resp = self._client.get(
                "https://api.bing.microsoft.com/v7.0/search",
                headers=headers, params=params
            )
            data = resp.json()

            for item in data.get("webPages", {}).get("value", []):
                results.append({
                    "title": item.get("name", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("snippet", ""),
                })
        except Exception as e:
            print(f"  [!] Bing API 搜索出错: {e}")

        return results

    # ==================== 获取页面详情 ====================

    def fetch_page_content(self, url: str, max_length: int = 3000) -> Optional[str]:
        """
        获取网页正文内容

        Args:
            url: 网页URL
            max_length: 最大返回字符数

        Returns:
            网页文本内容
        """
        try:
            resp = self._client.get(
                url,
                headers={"User-Agent": self._user_agent},
                timeout=10.0
            )
            resp.encoding = "utf-8"

            soup = BeautifulSoup(resp.text, "html.parser")

            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)
            text = "\n".join(line for line in text.split("\n") if len(line.strip()) > 10)

            return text[:max_length]
        except Exception as e:
            print(f"  [!] 获取页面内容失败 {url}: {e}")
            return None

    def close(self):
        """关闭HTTP客户端"""
        self._client.close()
