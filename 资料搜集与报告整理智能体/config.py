"""
配置文件 —— 支持多种国产大模型平台
根据实际情况选择并配置即可
"""

# ==================== LLM 平台配置 ====================
# 可选平台: "dashscope" (通义千问), "qianfan" (百度文心), "openai-compat" (通用兼容)
LLM_PROVIDER = "dashscope"

# ----- 阿里云通义千问 (DashScope) -----
# 获取地址: https://help.aliyun.com/document_detail/2712195.html
DASHSCOPE_API_KEY = ""
DASHSCOPE_MODEL = "qwen-turbo"  # 可选: qwen-turbo, qwen-plus, qwen-max

# ----- 百度千帆 (文心一言) -----
# 获取地址: https://console.bce.baidu.com/qianfan/
QIANFAN_API_KEY = ""
QIANFAN_SECRET_KEY = ""
QIANFAN_MODEL = "ernie-3.5-8k"

# ----- OpenAI 兼容接口 (智谱AI GLM 等) -----
# 智谱 AI: https://open.bigmodel.cn/
OPENAI_COMPAT_API_KEY = ""
OPENAI_COMPAT_BASE_URL = ""  # 例如 "https://open.bigmodel.cn/api/paas/v4/"
OPENAI_COMPAT_MODEL = ""

# ==================== 搜索配置 ====================
# 搜索源: "bing_html" (必应网页搜索,推荐,国内可用), "baidu" (百度), "duckduckgo", "bing" (必应API)
SEARCH_PROVIDER = "bing_html"
BING_API_KEY = ""  # 使用必应搜索时需要
SEARCH_RESULT_COUNT = 8  # 每次搜索返回的结果数

# ==================== 系统配置 ====================
# 输出编码
OUTPUT_ENCODING = "utf-8"

# 报告默认语言 (zh/en)
REPORT_LANGUAGE = "zh"

# 最大重试次数
MAX_RETRIES = 3
