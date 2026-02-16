import os
import sys
import logging
from datetime import datetime
from subscription_manager import SubscriptionManager
from news_fetcher import NewsFetcher
from ai_analyzer import AIAnalyzer
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
    logger.info("Daily RSS工具启动")
    
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
        ai_analyzer = AIAnalyzer()
        analysis_result = ai_analyzer.analyze_daily_news(news_items)
        
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
        ai_analyzer.clean_old_analysis()
        
        logger.info("Daily RSS工具执行完成")
        
    except Exception as e:
        logger.error(f"执行失败: {e}", exc_info=True)


def run_weekly_review():
    """运行周回顾"""
    logger.info("开始周回顾分析...")
    
    try:
        ai_analyzer = AIAnalyzer()
        analysis_result = ai_analyzer.analyze_weekly_news()
        
        if analysis_result:
            push_manager = PushManager()
            push_manager.send_weekly_analysis(analysis_result)
        
        logger.info("周回顾分析完成")
        
    except Exception as e:
        logger.error(f"周回顾失败: {e}", exc_info=True)


def run_monthly_review():
    """运行月回顾"""
    logger.info("开始月回顾分析...")
    
    try:
        ai_analyzer = AIAnalyzer()
        analysis_result = ai_analyzer.analyze_monthly_news()
        
        if analysis_result:
            push_manager = PushManager()
            push_manager.send_monthly_analysis(analysis_result)
        
        logger.info("月回顾分析完成")
        
    except Exception as e:
        logger.error(f"月回顾失败: {e}", exc_info=True)


def add_subscription(url, name=None):
    """添加订阅源"""
    logger.info(f"添加订阅源: {url}")
    
    try:
        subscription_manager = SubscriptionManager()
        success = subscription_manager.add_subscription(url, name)
        
        if success:
            logger.info(f"订阅源添加成功: {url}")
        else:
            logger.warning(f"订阅源添加失败: {url}")
        
    except Exception as e:
        logger.error(f"添加订阅源失败: {e}", exc_info=True)


def remove_subscription(subscription_id):
    """删除订阅源"""
    logger.info(f"删除订阅源: {subscription_id}")
    
    try:
        subscription_manager = SubscriptionManager()
        success = subscription_manager.remove_subscription(subscription_id)
        
        if success:
            logger.info(f"订阅源删除成功: {subscription_id}")
        else:
            logger.warning(f"订阅源删除失败: {subscription_id}")
        
    except Exception as e:
        logger.error(f"删除订阅源失败: {e}", exc_info=True)


def list_subscriptions():
    """列出所有订阅源"""
    logger.info("列出所有订阅源")
    
    try:
        subscription_manager = SubscriptionManager()
        subscriptions = subscription_manager.get_subscriptions()
        
        print("当前订阅源列表:")
        for sub in subscriptions:
            print(f"- ID: {sub['id']}")
            print(f"  名称: {sub['name']}")
            print(f"  URL: {sub['url']}")
            print(f"  类型: {sub['type']}")
            print(f"  最后更新: {sub['last_updated']}")
            print()
        
    except Exception as e:
        logger.error(f"列出订阅源失败: {e}", exc_info=True)


def test_ai_analysis():
    """独立测试AI分析功能"""
    logger.info("开始测试AI分析功能...")
    
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
                "content": "国际货币基金组织(IMF)近日上调了全球经济增长预期，预计今年全球经济将增长3.5%，高于此前预期的3.2%。这一调整主要基于全球通胀压力缓解、主要经济体货币政策趋于稳定以及新兴市场国家经济表现强劲等因素。IMF同时警告，地缘政治紧张局势和气候变化仍是全球经济面临的主要风险。",
                "source": "经济时报",
                "published_at": "2026-02-14T09:30:00Z",
                "collected_at": "2026-02-14T10:00:00Z"
            }
        ]
        
        print(f"模拟了 {len(mock_news)} 条新闻用于测试")
        
        # 创建AI分析器
        ai_analyzer = AIAnalyzer()
        
        # 测试单条新闻分析
        print("\n测试单条新闻分析:")
        single_news = mock_news[0]
        single_analysis = ai_analyzer._analyze_single_news(single_news)
        print(f"新闻标题: {single_analysis['title']}")
        print(f"分析摘要: {single_analysis['summary']}")
        print(f"关键词: {single_analysis['keywords']}")
        print(f"情感分析: {single_analysis['sentiment']}")
        
        # 测试并行分析
        print("\n测试并行分析:")
        analysis_results = ai_analyzer._parallel_analysis(mock_news)
        print(f"并行分析完成，共分析 {len(analysis_results)} 条新闻")
        
        # 测试生成分析报告
        print("\n测试生成分析报告:")
        daily_summary = ai_analyzer._generate_daily_summary(analysis_results)
        print("每日总结:")
        print(daily_summary)
        
        event_analysis = ai_analyzer._generate_event_analysis(analysis_results)
        print("\n事件分析:")
        print(event_analysis)
        
        logger.info("AI分析功能测试完成")
        
    except Exception as e:
        logger.error(f"测试AI分析功能失败: {e}", exc_info=True)


if __name__ == "__main__":
    # 解析命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "weekly":
            run_weekly_review()
        elif command == "monthly":
            run_monthly_review()
        elif command == "add":
            if len(sys.argv) > 2:
                url = sys.argv[2]
                name = sys.argv[3] if len(sys.argv) > 3 else None
                add_subscription(url, name)
            else:
                print("用法: python main.py add <url> [name]")
        elif command == "remove":
            if len(sys.argv) > 2:
                subscription_id = sys.argv[2]
                remove_subscription(subscription_id)
            else:
                print("用法: python main.py remove <subscription_id>")
        elif command == "list":
            list_subscriptions()
        elif command == "ai-test":
            test_ai_analysis()
        else:
            print(f"未知命令: {command}")
            print("可用命令: weekly, monthly, add, remove, list, ai-test")
    else:
        # 执行默认的每日任务
        main()
