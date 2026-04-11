"""
V2.0.0 集成测试
测试完整的四层分析流程到邮件渲染
"""
import os
import sys
import json
import time
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime
from push_manager import PushManager
from ai_analyzer_v2 import AIAnalyzerV2
from ai_analyzer_v2 import get_empty_structure, validate_v2_structure


def test_integration_with_mock_data():
    """使用模拟数据测试完整流程"""
    print("=" * 60)
    print("集成测试：完整 V2 流程（模拟数据）")
    print("=" * 60)

    # 1. 准备模拟新闻数据
    mock_news = [
        {"title": "OpenAI 宣布关停 AI 视频生成模型 Sora", "source": "科技日报", "content": "OpenAI 正式发布声明..."},
        {"title": "苹果被曝正开发 AI Siri，计划于 2026 年深度整合", "source": "彭博社", "content": "据知情人士透露..."},
        {"title": "国内油价全面进入 9 元时代", "source": "新华社", "content": "国家发改委宣布..."},
        {"title": "新一代迈巴赫 S 级亮相", "source": "汽车周刊", "content": "梅赛德斯 - 奔驰发布..."},
        {"title": "日产 Z Nismo 亮相，计划年内引进", "source": "汽车网", "content": "日产汽车宣布..."},
    ]

    print(f"\n1. 模拟新闻数据：{len(mock_news)} 条")

    # 2. 准备模拟的 V2 分析结果
    mock_analysis = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "timestamp": datetime.now().isoformat(),
        "news_count": len(mock_news),
        "summary": {
            "one_liner": "未来难料，AI 局势依旧充满变数",
            "digest": "AI 领域动态频发，Sora 关停引发行业震动，苹果、千问等巨头加速 AI 产品布局，同时油价上涨影响消费市场。",
            "keywords": ["震荡", "未知", "涨价"]
        },
        "key_news_brief": [
            {"title": "OpenAI 宣布关停 AI 视频生成模型 Sora", "tags": ["科技", "AI"]},
            {"title": "苹果被曝正开发 AI Siri", "tags": ["科技", "AI"]},
            {"title": "国内油价全面进入 9 元时代", "tags": ["经济", "民生"]}
        ],
        "briefing": {
            "politics": "油价全面进入 9 元时代，可能影响消费者出行选择与能源成本。分析师建议避开部分工业股。",
            "economy": "国内油价大幅上调，全国 92 号汽油均价突破 9 元/升，部分地区直接迈入 9 元时代。",
            "industry": "新一代迈巴赫 S 级及一款全新 MPV 亮相，日产 Z Nismo 亮相计划年内引进。",
            "tech": "OpenAI 宣布关停 AI 视频生成模型 Sora，苹果被曝正开发 AI Siri。"
        },
        "perspectives": [
            {
                "title": "告别流量与代码，拥抱认知与架构",
                "description": "AI 正在重塑商业与技术的底层逻辑。投资领域，旧日追逐 DAU 的神话已然失效，新的范式是寻找能理解 AI 底层逻辑的创业者。",
                "references": [
                    {"title": "AI 投资新范式", "url": "https://example.com/1"},
                    {"title": "代码已死？OpenAI 内部揭示", "url": "https://example.com/2"}
                ]
            },
            {
                "title": "AI 应用的寒冬还是春天",
                "description": "Sora 的关停揭示了一个残酷现实：技术先进不等于商业成功。AI 应用公司必须找到可持续的商业模式。",
                "references": [
                    {"title": "Sora 关停背后的商业逻辑", "url": "https://example.com/3"}
                ]
            },
            {
                "title": "能源转型的加速点",
                "description": "油价上涨可能成为新能源汽车消费的关键转折点。历史数据显示，当油价持续高位时，消费者更倾向于选择新能源汽车。",
                "references": [
                    {"title": "油价与新能源汽车消费关系研究", "url": "https://example.com/4"}
                ]
            }
        ],
        "deep_analysis": [
            {
                "tags": ["消费", "经济"],
                "title": "国内油价全面进入 9 元时代，或加速新能源汽车消费趋势",
                "facts": "根据国家发改委于 2026 年 3 月 23 日 24 时开启的调价窗口，国内汽油、柴油价格每吨分别上调 2000 元、2050 元。",
                "viewpoint": "新闻的重点在于油价大幅上涨对居民消费成本的直接影响，以及由此可能引发的消费者购车选择变化。",
                "causes": "本次油价调整有明确主体——国家发改委，遵循既定的成品油价格形成机制。",
                "prediction": "预计油价将维持高位震荡，新能源汽车渗透率将持续提升。",
                "advice": "投资：关注新能源汽车产业链龙头企业。消费：认真对比燃油车与新能源汽车的全生命周期使用成本。"
            },
            {
                "tags": ["AI", "科技"],
                "title": "苹果被曝正开发 AI Siri，计划于 2026 年深度整合",
                "facts": "据曝料，苹果正在开发全新的 AI Siri，计划于 2026 年深度整合到 iPhone 中。",
                "viewpoint": "这标志着智能手机进入 AI 原生时代，传统应用生态可能面临重构。",
                "causes": "生成式 AI 的快速发展推动了智能手机厂商的 AI 布局。",
                "prediction": "2026 年 iPhone 将成为 AI 原生设备，传统 App 使用频率可能大幅下降。",
                "advice": "投资者关注 AI 手机产业链，开发者应提前布局 AI 原生应用开发。"
            },
            {
                "tags": ["AI", "商业"],
                "title": "OpenAI 宣布关停 AI 视频生成模型 Sora",
                "facts": "OpenAI 正式宣布关停 Sora 项目，这款曾被视为 AI 视频生成标杆的产品从发布到关停仅运营七个月。",
                "viewpoint": "Sora 的关停揭示了 AI 视频生成的商业化困境：技术先进但商业模式不清晰。",
                "causes": "高昂的算力成本、有限的商业化场景、激烈的市场竞争共同导致了 Sora 的失败。",
                "prediction": "AI 视频生成行业将进入整合期，只有找到清晰商业模式的公司才能生存。",
                "advice": "投资者需谨慎评估 AI 视频公司的商业模式，避免纯概念炒作。"
            }
        ],
        "suggestions": {
            "thinking": {
                "title": "技术理想与商业现实的鸿沟",
                "content": "Sora 的关停揭示了一个重要教训：技术先进性必须与商业可行性相结合。投资者和创业者都需要重新评估 AI 项目的价值主张。"
            },
            "investment": {
                "title": "投资思路应更注重务实、结构和抗周期性",
                "content": "拥抱确定性趋势，规避纯概念炒作：\n\n1. 新能源汽车产业链：油价高企是长期利好。\n2. AI 的'卖水人'与'工具匠'：为 AI 提供算力的企业。\n3. 规避：商业模式不清晰的纯技术型 AI 公司。"
            },
            "self_improvement": {
                "title": "个人能力需要同步升级",
                "content": "从'操作工'转向'架构师'与'协作者'：\n\n1. 掌握与 AI 协作的高阶技能：提示词工程、AI 工作流设计。\n2. 深化垂直领域知识：行业专家+AI 工具的组合将极具竞争力。"
            },
            "opportunities_risks": {
                "title": "机遇与风险并存",
                "content": "机遇：新能源转型、AI 原生应用。\n风险：纯概念炒作、高估值低收入的 AI 公司。"
            }
        }
    }

    # 3. 验证数据结构
    print("\n2. 验证 V2 数据结构...")
    is_valid, errors = validate_v2_structure(mock_analysis)
    if is_valid:
        print("   ✓ 数据结构验证通过")
    else:
        print(f"   ✗ 数据结构验证失败：{errors}")
        return False

    # 4. 测试邮件渲染
    print("\n3. 测试邮件渲染...")
    start_time = time.time()
    push_manager = PushManager()

    try:
        html_content = push_manager._generate_v2_html_content(mock_analysis)
        render_time = time.time() - start_time
        print(f"   ✓ 渲染成功，耗时：{render_time:.3f}秒")
        print(f"   ✓ HTML 大小：{len(html_content)} 字节")
    except Exception as e:
        print(f"   ✗ 渲染失败：{e}")
        return False

    # 5. 验证渲染内容
    print("\n4. 验证渲染内容...")
    checks = [
        ("DOCTYPE 声明", "<!DOCTYPE html>" in html_content),
        ("Header 板块", 'class="header"' in html_content),
        ("Today Brief", 'class="today-brief"' in html_content),
        ("新闻列表", 'class="news-list"' in html_content),
        ("观点板块", 'class="opinion-section"' in html_content),
        ("分析板块", 'class="insight-section"' in html_content),
        ("建议板块", 'class="advice-section"' in html_content),
        ("关键词样式", 'class="keyword-item"' in html_content),
        ("观点项", 'class="opinion-item"' in html_content),
        ("分析项", 'class="insight-item"' in html_content),
        ("建议项", 'class="advice-item"' in html_content),
        ("CSS 变量", '--brand:' in html_content or '--brand: ' in html_content),
        ("响应式设计", '@media' in html_content),
    ]

    all_passed = True
    for name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"   {status} {name}")
        if not passed:
            all_passed = False

    # 6. 保存渲染结果
    print("\n5. 保存渲染结果...")
    output_path = os.path.join(os.path.dirname(__file__), 'integration_test_output.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"   ✓ 输出文件：{output_path}")

    # 7. 性能检查
    print("\n6. 性能检查...")
    expected_size_min = 10000  # 至少 10KB
    if len(html_content) >= expected_size_min:
        print(f"   ✓ HTML 大小达标：{len(html_content)} 字节 >= {expected_size_min} 字节")
    else:
        print(f"   ✗ HTML 大小不足：{len(html_content)} 字节 < {expected_size_min} 字节")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("集成测试通过 ✓")
    else:
        print("集成测试失败 ✗")
    print("=" * 60)

    return all_passed


def test_schema_validation():
    """测试 Schema 验证功能"""
    print("\n" + "=" * 60)
    print("Schema 验证测试")
    print("=" * 60)

    # 测试有效数据
    valid_data = {
        "summary": {"one_liner": "t", "digest": "t", "keywords": ["k"]},
        "key_news_brief": [],
        "briefing": {"politics": "", "economy": "", "industry": "", "tech": ""},
        "perspectives": [],
        "deep_analysis": [],
        "suggestions": {
            "thinking": {"title": "", "content": ""},
            "investment": {"title": "", "content": ""},
            "self_improvement": {"title": "", "content": ""},
            "opportunities_risks": {"title": "", "content": ""}
        }
    }

    is_valid, errors = validate_v2_structure(valid_data)
    print(f"最小有效结构：{'✓ 通过' if is_valid else '✗ 失败'}")

    # 测试空结构
    empty = get_empty_structure()
    is_valid, errors = validate_v2_structure(empty)
    print(f"空结构：{'✓ 通过' if is_valid else '✗ 失败'}")

    # 测试无效数据
    invalid_data = {"summary": {"one_liner": "t"}}  # 缺少必需字段
    is_valid, errors = validate_v2_structure(invalid_data)
    print(f"无效数据检测：{'✓ 正确拒绝' if not is_valid else '✗ 未检测到错误'}")

    return True


if __name__ == "__main__":
    print("V2.0.0 集成测试套件")
    print(f"运行时间：{datetime.now().isoformat()}")

    # 运行 Schema 验证测试
    test_schema_validation()

    # 运行完整集成测试
    success = test_integration_with_mock_data()

    if success:
        print("\n✅ 所有集成测试通过")
        sys.exit(0)
    else:
        print("\n❌ 部分集成测试失败")
        sys.exit(1)
