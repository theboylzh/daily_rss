"""
V2.0.0 输出 JSON Schema 定义
"""
from typing import List, Dict, Any


# 预设标签库
TAGS_LIBRARY = [
    "政治",      # 政府、政策、国际关系
    "经济",      # 宏观经济、GDP、通胀
    "科技",      # 技术突破、前沿科技
    "商业",      # 公司动态、商业合作
    "金融",      # 银行、证券、保险
    "国际",      # 国际时事
    "政策",      # 行业政策、监管
    "创新",      # 新产品、新技术
    "行业",      # 行业动态、供需变化
    "市场"       # 市场波动、股价变化
]


def get_empty_structure() -> Dict[str, Any]:
    """返回空的 V2 输出结构，用于降级处理"""
    return {
        "summary": {
            "one_liner": "今日暂无新闻摘要",
            "digest": "今日暂无新闻内容",
            "keywords": ["暂无", "暂无", "暂无"]
        },
        "key_news_brief": [],
        "briefing": {
            "politics": "暂无政治新闻",
            "economy": "暂无经济新闻",
            "industry": "暂无行业新闻",
            "tech": "暂无科技新闻"
        },
        "perspectives": [],
        "deep_analysis": [],
        "suggestions": {
            "thinking": {"title": "暂无", "content": "暂无相关思维启发"},
            "investment": {"title": "暂无", "content": "暂无相关投资建议"},
            "self_improvement": {"title": "暂无", "content": "暂无相关个人提升建议"},
            "opportunities_risks": {"title": "暂无", "content": "暂无相关机遇风险提示"}
        }
    }


# V2 输出 Schema 说明文档
V2_SCHEMA_DESCRIPTION = """
V2.0.0 输出 JSON Schema:

{
  "summary": {                    # 阶段 1 输出
    "one_liner": string,          # 一句话总结（20-30 字，抽象理性）
    "digest": string,             # 今日摘要（2-3 句话）
    "keywords": [string]          # 三个关键词
  },
  "key_news_brief": [             # 阶段 1 输出，3 条关键新闻
    {"title": string, "tags": [string]}
  ],
  "briefing": {                   # 阶段 1 输出
    "politics": string,           # 政治时事
    "economy": string,            # 宏观经济
    "industry": string,           # 行业动态
    "tech": string                # 科技新闻
  },
  "perspectives": [               # 阶段 2 输出，3 个观点
    {
      "title": string,
      "description": string,
      "references": [{"title": string, "url": string}]
    }
  ],
  "deep_analysis": [              # 阶段 3 输出，3 个事件分析
    {
      "tags": [string],
      "title": string,
      "facts": string,
      "viewpoint": string,
      "causes": string,
      "prediction": string,
      "advice": string
    }
  ],
  "suggestions": {                # 阶段 4 输出
    "thinking": {"title": string, "content": string},
    "investment": {"title": string, "content": string},
    "self_improvement": {"title": string, "content": string},
    "opportunities_risks": {"title": string, "content": string}
  }
}
"""
