import os
import sys
import logging
import traceback
from datetime import datetime
from subscription_manager import SubscriptionManager
from news_fetcher import NewsFetcher
from ai_analyzer_v2 import AIAnalyzerV2
from push_manager import PushManager
from config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rss_tool.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """主程序入口"""
    logger.info("Daily RSS 工具启动")

    try:
        # 1. 抓取新闻
        logger.info("开始抓取新闻...")
        news_fetcher = NewsFetcher()
        news_items = news_fetcher.fetch_news()

        if not news_items:
            logger.warning("无新闻可分析")
            return

        # 2. 分析新闻
        logger.info("开始分析新闻...")
        ai_analyzer = AIAnalyzerV2()
        analysis_result = ai_analyzer.analyze_daily_news_v2(news_items)

        if not analysis_result:
            logger.warning("分析失败")
            return

        # 3. 推送分析结果
        logger.info("开始推送分析结果...")
        push_manager = PushManager()
        push_success = push_manager.send_daily_analysis(analysis_result)

        if not push_success:
            logger.warning("推送失败")
            return

        # 4. 清理过期数据
        logger.info("开始清理过期数据...")
        news_fetcher.clean_old_news()

        logger.info("Daily RSS 工具执行完成")

    except Exception as e:
        logger.error(f"执行失败：{e}", exc_info=True)
        # 尝试发送错误通知邮件
        try:
            push_manager = PushManager()
            error_analysis = {
                "date": datetime.now().strftime('%Y-%m-%d'),
                "first_layer": f"# 执行错误\n\n系统执行失败：{str(e)}",
                "second_layer": [],
                "third_layer": f"# 错误详情\n\n{traceback.format_exc()}",
                "timestamp": datetime.now().isoformat(),
                "news_count": 0
            }
            push_manager.send_daily_analysis(error_analysis)
        except Exception as notify_error:
            logger.error(f"发送错误通知失败：{notify_error}")



def add_subscription(url, name=None):
    """添加订阅源"""
    logger.info(f"添加订阅源：{url}")

    try:
        subscription_manager = SubscriptionManager()
        success = subscription_manager.add_subscription(url, name)

        if success:
            logger.info(f"订阅源添加成功：{url}")
        else:
            logger.warning(f"订阅源添加失败：{url}")

    except Exception as e:
        logger.error(f"添加订阅源失败：{e}", exc_info=True)


def remove_subscription(subscription_id):
    """删除订阅源"""
    logger.info(f"删除订阅源：{subscription_id}")

    try:
        subscription_manager = SubscriptionManager()
        success = subscription_manager.remove_subscription(subscription_id)

        if success:
            logger.info(f"订阅源删除成功：{subscription_id}")
        else:
            logger.warning(f"订阅源删除失败：{subscription_id}")

    except Exception as e:
        logger.error(f"删除订阅源失败：{e}", exc_info=True)


def list_subscriptions():
    """列出所有订阅源"""
    logger.info("列出所有订阅源")

    try:
        subscription_manager = SubscriptionManager()
        subscriptions = subscription_manager.get_subscriptions()

        print("当前订阅源列表:")
        for sub in subscriptions:
            print(f"- ID: {sub['id']}")
            print(f"  名称：{sub['name']}")
            print(f"  URL: {sub['url']}")
            print(f"  类型：{sub['type']}")
            print(f"  最后更新：{sub['last_updated']}")
            print()

    except Exception as e:
        logger.error(f"列出订阅源失败：{e}", exc_info=True)


def test_ai_analysis():
    """独立测试 AI 分析功能（V2）"""
    logger.info("开始测试 AI 分析功能...")

    try:
        # 模拟新闻数据
        mock_news = [
            {
                "id": "1",
                "title": "人工智能技术取得重大突破",
                "url": "https://example.com/news1",
                "content": "近日，人工智能技术在自然语言处理和计算机视觉领域取得重大突破。研究人员开发了一种新的深度学习模型，能够更准确地理解和生成人类语言，同时在图像识别方面也有显著提升。这项技术的应用前景广阔，有望在医疗、教育、金融等多个领域发挥重要作用。",
                "source": "科技日报",
                "published_at": "2026-02-14T08:00:00Z",
                "collected_at": "2026-02-14T09:00:00Z"
            },
            {
                "id": "2",
                "title": "全球经济增长预期上调",
                "url": "https://example.com/news2",
                "content": "国际货币基金组织 (IMF) 近日上调了全球经济增长预期，预计今年全球经济将增长 3.5%，高于此前预期的 3.2%。这一调整主要基于全球通胀压力缓解、主要经济体货币政策趋于稳定以及新兴市场国家经济表现强劲等因素。IMF 同时警告，地缘政治紧张局势和气候变化仍是全球经济面临的主要风险。",
                "source": "经济时报",
                "published_at": "2026-02-14T09:30:00Z",
                "collected_at": "2026-02-14T10:00:00Z"
            }
        ]

        print(f"模拟了 {len(mock_news)} 条新闻用于测试")

        # 创建 AI 分析器（V2）
        ai_analyzer = AIAnalyzerV2()

        # 测试完整的每日分析（V2 四层架构）
        print("\n测试完整的每日分析（V2 四层架构）:")
        analysis_result = ai_analyzer.analyze_daily_news_v2(mock_news)
        print(f"分析完成，结果包含：{list(analysis_result.keys())}")

        # 打印 V2 分析结果
        print(f"\n【一句话总结】")
        print(analysis_result.get('summary', {}).get('one_liner', '缺失'))

        print(f"\n【关键词】")
        print(analysis_result.get('summary', {}).get('keywords', []))

        print(f"\n【关键新闻】")
        for i, news in enumerate(analysis_result.get('key_news_brief', [])[:3], 1):
            print(f"  {i}. {news.get('title', '无标题')}")

        print(f"\n【观点】")
        for i, p in enumerate(analysis_result.get('perspectives', [])[:3], 1):
            print(f"  {i}. {p.get('title', '无标题')}")

        print(f"\n【深度分析】")
        for i, a in enumerate(analysis_result.get('deep_analysis', [])[:3], 1):
            print(f"  {i}. {a.get('title', '无标题')}")

        print(f"\n【建议】")
        suggestions = analysis_result.get('suggestions', {})
        print(f"  思维启发：{suggestions.get('thinking', {}).get('title', '缺失')}")
        print(f"  投资建议：{suggestions.get('investment', {}).get('title', '缺失')}")

        logger.info("AI 分析功能测试完成")

    except Exception as e:
        logger.error(f"测试 AI 分析功能失败：{e}", exc_info=True)


if __name__ == "__main__":
    # 解析命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "add":
            if len(sys.argv) > 2:
                url = sys.argv[2]
                name = sys.argv[3] if len(sys.argv) > 3 else None
                add_subscription(url, name)
            else:
                print("用法：python main.py add <url> [name]")
        elif command == "remove":
            if len(sys.argv) > 2:
                subscription_id = sys.argv[2]
                remove_subscription(subscription_id)
            else:
                print("用法：python main.py remove <subscription_id>")
        elif command == "list":
            list_subscriptions()
        elif command == "ai-test":
            test_ai_analysis()
        else:
            print(f"未知命令：{command}")
            print("可用命令：add, remove, list, ai-test")
    else:
        # 执行默认的每日任务
        main()
