"""
分析智能体 —— 利用大模型对搜集的资料进行理解和分析
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AnalysisAgent:
    """分析智能体：使用大模型分析资料并提取关键信息"""

    def __init__(self, provider: str = "dashscope",
                 api_key: str = None,
                 model: str = None):
        """
        初始化分析智能体

        Args:
            provider: 模型供应商
            api_key: API密钥
            model: 模型名称
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self._client = None

        if provider != "mock":
            self._init_llm_client()

    def _init_llm_client(self):
        """初始化LLM客户端"""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "请安装 openai 库: pip install openai"
            )

        if self.provider == "dashscope":
            # 阿里通义千问 (兼容 OpenAI API)
            self._client = OpenAI(
                api_key=self.api_key or os.getenv("DASHSCOPE_API_KEY", ""),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
            self.model = self.model or "qwen-turbo"

        elif self.provider == "qianfan":
            # 百度千帆
            import httpx
            self._qianfan_api_key = self.api_key or os.getenv("QIANFAN_API_KEY", "")
            self._qianfan_secret_key = os.getenv("QIANFAN_SECRET_KEY", "")
            self._qianfan_access_token = self._get_qianfan_token()
            self._client_httpx = httpx.Client(timeout=60.0)
            self._qianfan_base = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat"
            self.model = self.model or "ernie-3.5-8k"

        elif self.provider == "openai-compat":
            self._client = OpenAI(
                api_key=self.api_key or os.getenv("OPENAI_COMPAT_API_KEY", ""),
                base_url=os.getenv("OPENAI_COMPAT_BASE_URL", ""),
            )
            self.model = self.model or os.getenv("OPENAI_COMPAT_MODEL", "")

    def _get_qianfan_token(self) -> str:
        """获取百度千帆 access_token"""
        import httpx
        resp = httpx.post(
            "https://aip.baidubce.com/oauth/2.0/token",
            params={
                "grant_type": "client_credentials",
                "client_id": self._qianfan_api_key,
                "client_secret": self._qianfan_secret_key,
            }
        )
        return resp.json().get("access_token", "")

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        调用大模型

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词

        Returns:
            模型回复文本
        """
        if self.provider == "mock":
            return self._mock_llm_response(user_prompt)

        try:
            if self.provider == "dashscope":
                resp = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3,
                    max_tokens=4096,
                )
                return resp.choices[0].message.content or ""

            elif self.provider == "qianfan":
                model_endpoints = {
                    "ernie-3.5-8k": "completions",
                    "ernie-4.0-8k": "ernie-4.0-8k",
                }
                endpoint = model_endpoints.get(self.model, "completions")
                resp = self._client_httpx.post(
                    f"{self._qianfan_base}/{endpoint}",
                    params={"access_token": self._qianfan_access_token},
                    json={
                        "messages": [
                            {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"},
                        ],
                        "temperature": 0.3,
                        "max_output_tokens": 4096,
                    }
                )
                return resp.json().get("result", "")

            elif self.provider == "openai-compat":
                resp = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3,
                    max_tokens=4096,
                )
                return resp.choices[0].message.content or ""

        except Exception as e:
            return f"[调用大模型时出错: {e}]"

    def _mock_llm_response(self, prompt: str) -> str:
        """模拟 LLM 回复（用于无 API 密钥时的演示）"""
        return (
            "【模拟分析结果】\n\n"
            "基于搜集到的资料，以下是分析结果：\n\n"
            "1. **核心概念**\n"
            "   该主题涉及多个关键领域，包括技术实现、应用场景和发展趋势。\n"
            "   目前学术界和产业界对此给予了高度关注。\n\n"
            "2. **主要发现**\n"
            "   - 该领域正处于快速发展阶段\n"
            "   - 多项研究表明其应用前景广阔\n"
            "   - 存在若干关键技术挑战需要克服\n\n"
            "3. **趋势分析**\n"
            "   从发展趋势来看，该领域未来将朝着更智能化、更高效的方向发展，\n"
            "   预计在未来3-5年内将取得重要突破。\n\n"
            "4. **应用案例**\n"
            "   目前已有多个成功应用案例，涵盖不同行业和场景，\n"
            "   证明了该技术的普适性和实用价值。\n\n"
            "---\n"
            "*注：此为模拟输出。配置有效的 API 密钥后可获得真实分析结果。*"
        )

    def analyze_materials(self, materials: dict) -> dict:
        """
        分析搜集到的资料

        Args:
            materials: 搜索智能体收集的原始资料

        Returns:
            分析结果
        """
        topic = materials.get("topic", "未知主题")
        snippets = "\n\n".join(
            f"来源{i+1}: {s['title']}\n链接: {s['url']}\n摘要: {s['snippet']}"
            for i, s in enumerate(materials.get("sources", [])[:10])
        )

        raw_contents = ""
        for i, c in enumerate(materials.get("raw_contents", [])[:5]):
            raw_contents += f"\n\n--- 页面{i+1}: {c['title']} ---\n{c['content'][:2000]}"

        print(f"\n  [ANALYSIS] 开始分析资料...")
        print(f"  [ANALYSIS] 信息来源数: {len(materials.get('sources', []))}")
        print(f"  [ANALYSIS] 详细页面数: {len(materials.get('raw_contents', []))}")

        # 分析资料
        system_prompt = """你是一个专业的资料分析助手。你的任务是对搜集到的资料进行深入分析，提取关键信息，并形成结构化分析报告。
请从以下维度进行分析：
1. 核心概念与定义
2. 主要研究/应用方向
3. 关键技术与方法
4. 典型案例与应用场景
5. 发展趋势与前景
6. 挑战与问题

请用中文回答，分析要深入、客观、结构清晰。"""

        user_prompt = f"""请对以下关于「{topic}」的资料进行深入分析：

## 搜索结果摘要
{snippets}

## 详细页面内容
{raw_contents}

请提供结构化的分析报告，包含核心概念、主要方向、关键技术、典型案例、发展趋势和面临的挑战。"""

        analysis_text = self._call_llm(system_prompt, user_prompt)

        # 提取关键词（失败时有默认值）
        try:
            kw_system_prompt = "你是一个关键词提取助手。请从给定文本中提取3-5个最相关的关键词，以逗号分隔输出。"
            kw_result = self._call_llm(kw_system_prompt, f"请从以下分析中提取关键词：\n\n{analysis_text[:2000]}")
            if kw_result.startswith("[调用大模型时出错"):
                keywords = ["人工智能", "机器学习", "自然语言处理", "数据分析", "智能体"]
            else:
                keywords = [k.strip() for k in kw_result.strip().split("，") if k.strip()]
        except Exception:
            keywords = ["人工智能", "机器学习", "自然语言处理", "数据分析", "智能体"]

        print(f"  [OK] 分析完成！")

        return {
            "topic": topic,
            "analysis": analysis_text,
            "keywords": keywords[:8] or ["人工智能", "机器学习", "数据分析"],
            "source_count": len(materials.get("sources", [])),
        }

    def close(self):
        """释放资源"""
        if hasattr(self, '_client_httpx'):
            self._client_httpx.close()
