import os
import sys
import logging
from datetime import datetime
from push_manager import PushManager

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

def test_email_sending():
    """测试邮件发送功能"""
    logger.info("开始测试邮件发送功能...")
    
    try:
        # 模拟分析结果
        mock_analysis = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "first_layer": "# 测试邮件\n\n这是一封测试邮件，用于验证GitHub Action自动化运行时的邮件发送功能。",
            "second_layer": [],
            "third_layer": "# 测试内容\n\n如果您收到这封邮件，说明邮件发送功能正常。",
            "timestamp": datetime.now().isoformat(),
            "news_count": 1
        }
        
        # 创建推送管理器
        push_manager = PushManager()
        
        # 发送测试邮件
        push_success = push_manager.send_daily_analysis(mock_analysis)
        
        if push_success:
            logger.info("测试邮件发送成功")
            print("测试邮件发送成功")
        else:
            logger.error("测试邮件发送失败")
            print("测试邮件发送失败")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"测试邮件发送失败: {e}", exc_info=True)
        print(f"测试邮件发送失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_email_sending()