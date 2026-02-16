import os
import json
import time
import ssl
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Any
from subscription_manager import SubscriptionManager
from config import settings


class NewsFetcher:
    def __init__(self):
        self.subscription_manager = SubscriptionManager()
        self.news_dir = settings.NEWS_DIR
        os.makedirs(self.news_dir, exist_ok=True)
        
        # RSSHub实例列表，按优先级排序
        self.rsshub_instances = [
            "https://rss.owo.nz",
            "https://rsshub.rssforever.com",
            "https://hub.slarker.me",
            "https://rsshub.pseudoyu.com",
            "https://rsshub.ktachibana.party",
            "https://rsshub.umzzz.com",
            "https://rss.spriple.org"
        ]
    
    def fetch_news(self) -> List[Dict[str, Any]]:
        """抓取所有订阅源的新闻"""
        subscriptions = self.subscription_manager.get_subscriptions()
        all_news = []
        
        for subscription in subscriptions:
            try:
                print(f"抓取订阅源: {subscription['name']}")
                news_items = self._fetch_from_subscription(subscription)
                all_news.extend(news_items)
                
                # 更新订阅源的最后更新时间
                self.subscription_manager.update_subscription_timestamp(
                    subscription['id'], datetime.now().isoformat()
                )
            except Exception as e:
                print(f"抓取订阅源失败 {subscription['name']}: {e}")
        
        # 去重
        unique_news = self._deduplicate_news(all_news)
        
        # 过滤24小时内的新闻
        recent_news = self._filter_recent_news(unique_news)
        
        # 存储新闻
        self._save_news(recent_news)
        
        print(f"抓取完成，共获取 {len(recent_news)} 条新闻")
        return recent_news
    
    def _fetch_from_subscription(self, subscription: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从单个订阅源抓取新闻"""
        original_url = subscription['url']
        
        # 检测是否是RSSHub URL
        is_rsshub = self._is_rsshub_url(original_url)
        
        # 准备要尝试的URL列表
        urls_to_try = [original_url]
        
        # 如果是RSSHub URL，添加其他实例的URL
        if is_rsshub:
            print(f"检测到RSSHub URL: {original_url}")
            # 为每个RSSHub实例创建一个URL
            for instance in self.rsshub_instances:
                # 跳过原始实例
                if instance in original_url:
                    continue
                # 创建新的URL
                new_url = self._replace_rsshub_instance(original_url, instance)
                urls_to_try.append(new_url)
            print(f"准备尝试 {len(urls_to_try)} 个RSSHub实例")
        
        # 使用feedparser抓取RSS内容，添加超时和重试机制
        max_retries = 3
        retry_delay = 2  # 秒
        
        # 尝试每个URL
        for url in urls_to_try:
            print(f"\n尝试使用URL: {url}")
            
            for attempt in range(max_retries):
                try:
                    print(f"抓取订阅源 {subscription['name']} (尝试 {attempt+1}/{max_retries})...")
                    
                    # 确保导入feedparser
                    import feedparser
                    
                    # 优先使用feedparser直接解析URL（更可靠）
                    try:
                        print(f"尝试使用feedparser直接解析URL...")
                        
                        # 设置feedparser的超时和请求头
                        import socket
                        socket.setdefaulttimeout(30)  # 30秒超时
                        
                        # 为feedparser添加请求头
                        feedparser.USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
                        
                        # 添加请求头
                        request_headers = {
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                            'Connection': 'keep-alive'
                        }
                        
                        # 为 rsshub 添加特殊处理
                        if 'rsshub' in url:
                            print("为 rsshub 添加特殊请求头...")
                            request_headers.update({
                                'Referer': 'https://rsshub.app/',
                                'Origin': 'https://rsshub.app'
                            })
                        
                        # 使用feedparser抓取RSS内容
                        feed = feedparser.parse(url, request_headers=request_headers)
                        
                        # 检查解析结果
                        if len(feed.entries) > 0:
                            print(f"✅ feedparser直接解析成功，获取到 {len(feed.entries)} 条新闻")
                        else:
                            # 如果feedparser直接解析失败，尝试使用requests获取内容
                            print(f"⚠️ feedparser直接解析获取到 {len(feed.entries)} 条新闻，尝试使用requests获取...")
                            
                            # 创建SSL上下文，忽略一些常见的SSL验证问题
                            import ssl
                            ssl_context = ssl.create_default_context()
                            ssl_context.check_hostname = False
                            ssl_context.verify_mode = ssl.CERT_NONE
                            
                            # 添加浏览器 User-Agent 和必要的请求头
                            headers = {
                                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                                'Connection': 'keep-alive',
                                'Upgrade-Insecure-Requests': '1'
                            }
                            
                            # 为 rsshub 添加特殊处理
                            if 'rsshub' in url:
                                print("尝试获取 rsshub 内容...")
                                headers['Referer'] = 'https://rsshub.app/'
                                headers['Origin'] = 'https://rsshub.app'
                            
                            # 使用requests获取内容（禁用压缩以避免乱码问题）
                            response = requests.get(url, timeout=30, verify=False, headers=headers, stream=True)
                            
                            # 详细调试信息
                            print(f"请求状态码: {response.status_code}")
                            
                            response.raise_for_status()
                            
                            # 读取原始内容并手动处理
                            content = response.raw.read()
                            
                            # 尝试不同的编码
                            encodings = ['utf-8', 'gbk', 'iso-8859-1']
                            parsed_content = None
                            
                            for encoding in encodings:
                                try:
                                    parsed_content = content.decode(encoding)
                                    print(f"✅ 成功使用 {encoding} 解码内容")
                                    break
                                except UnicodeDecodeError:
                                    print(f"❌ 使用 {encoding} 解码失败")
                                    continue
                            
                            if parsed_content:
                                # 使用feedparser解析内容
                                feed = feedparser.parse(parsed_content)
                            else:
                                print("❌ 所有编码尝试都失败")
                                feed = {}
                    except Exception as e:
                        # 如果获取内容失败，回退到简单的feedparser方法
                        print(f"❌ 获取内容失败，使用简单feedparser方法: {e}")
                        feed = feedparser.parse(url)
                    
                    # 检查是否有错误
                    if 'bozo_exception' in feed:
                        bozo_error = feed['bozo_exception']
                        error_type = type(bozo_error).__name__
                        print(f"❌ 解析警告 {url}: [{error_type}] {bozo_error}")
                    
                    news_items = []
                    for entry in feed.entries:
                        news_item = {
                            "id": self._generate_id(entry.link if 'link' in entry else entry.id),
                            "title": entry.title if 'title' in entry else "",
                            "url": entry.link if 'link' in entry else "",
                            "content": self._extract_content(entry),
                            "source": subscription['name'],
                            "published_at": self._parse_published_date(entry),
                            "collected_at": datetime.now().isoformat()
                        }
                        news_items.append(news_item)
                    
                    if len(news_items) > 0:
                        print(f"✅ 成功抓取 {len(news_items)} 条新闻 from {subscription['name']} (URL: {url})")
                        return news_items
                    else:
                        print(f"❌ 抓取订阅源 {subscription['name']} 失败：未获取到新闻")
                
                except socket.timeout:
                    print(f"❌ 抓取超时 {url}，{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                    
                except requests.exceptions.RequestException as e:
                    error_type = type(e).__name__
                    print(f"❌ 网络请求失败 {url}: [{error_type}] {e}")
                    if attempt < max_retries - 1:
                        print(f"{retry_delay}秒后重试...")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        print(f"❌ 所有尝试都失败，尝试下一个URL")
                        break
                        
                except ssl.SSLError as e:
                    error_type = type(e).__name__
                    print(f"❌ SSL错误 {url}: [{error_type}] {e}")
                    if attempt < max_retries - 1:
                        print(f"{retry_delay}秒后重试...")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        print(f"❌ 所有尝试都失败，尝试下一个URL")
                        break
                        
                except Exception as e:
                    error_type = type(e).__name__
                    print(f"❌ 抓取失败 {url}: [{error_type}] {e}")
                    if attempt < max_retries - 1:
                        print(f"{retry_delay}秒后重试...")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        print(f"❌ 所有尝试都失败，尝试下一个URL")
                        break
        
        print(f"❌ 所有URL都尝试失败，跳过此订阅源")
        return []
    
    def _extract_content(self, entry: Any) -> str:
        """提取新闻内容"""
        # 尝试从不同字段获取内容
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value
        elif hasattr(entry, 'summary'):
            content = entry.summary
        else:
            content = ""
        
        # 清理HTML标签
        soup = BeautifulSoup(content, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    
    def _parse_published_date(self, entry: Any) -> str:
        """解析发布日期"""
        if hasattr(entry, 'published') and entry.published:
            try:
                # 尝试直接解析ISO格式
                try:
                    published = datetime.fromisoformat(entry.published.replace('Z', '+00:00'))
                    return published.isoformat()
                except Exception:
                    # 尝试使用feedparser的内置日期解析
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                        return published.isoformat()
                    # 尝试其他常见格式
                    try:
                        import dateutil.parser
                        published = dateutil.parser.parse(entry.published)
                        return published.isoformat()
                    except ImportError:
                        # 如果没有dateutil库，使用更简单的方法
                        print("警告: dateutil库未安装，使用简单日期解析")
                        # 尝试几种常见格式
                        formats = ['%a, %d %b %Y %H:%M:%S %Z', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S']
                        for fmt in formats:
                            try:
                                published = datetime.strptime(entry.published, fmt)
                                return published.isoformat()
                            except Exception:
                                continue
            except Exception as e:
                print(f"日期解析失败: {e}")
                pass
        # 对于没有发布日期或解析失败的情况，返回24小时前的时间
        # 这样可以确保这些新闻会在下次抓取时被过滤掉
        return (datetime.now() - timedelta(hours=25)).isoformat()
    
    def _generate_id(self, url: str) -> str:
        """根据URL生成唯一ID"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()
    
    def _deduplicate_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重新闻"""
        seen_ids = set()
        unique_news = []
        
        for news in news_items:
            if news['id'] not in seen_ids:
                seen_ids.add(news['id'])
                unique_news.append(news)
        
        return unique_news
    
    def _filter_recent_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤24小时内的新闻"""
        threshold = datetime.now() - timedelta(hours=24)
        recent_news = []
        
        for news in news_items:
            try:
                published_at = datetime.fromisoformat(news['published_at'])
                if published_at >= threshold:
                    recent_news.append(news)
            except Exception:
                # 如果日期解析失败，默认保留
                recent_news.append(news)
        
        return recent_news
    
    def _save_news(self, news_items: List[Dict[str, Any]]):
        """保存新闻到文件"""
        today = datetime.now().strftime('%Y-%m-%d')
        news_file = os.path.join(self.news_dir, f"{today}.json")
        
        # 读取现有新闻（如果有）
        existing_news = []
        if os.path.exists(news_file):
            try:
                with open(news_file, 'r', encoding='utf-8') as f:
                    existing_news = json.load(f)
            except Exception as e:
                print(f"读取现有新闻失败: {e}")
        
        # 合并新闻并去重
        all_news = existing_news + news_items
        unique_news = self._deduplicate_news(all_news)
        
        # 保存到文件
        with open(news_file, 'w', encoding='utf-8') as f:
            json.dump(unique_news, f, ensure_ascii=False, indent=2)
    
    def get_recent_news(self, days: int = 1) -> List[Dict[str, Any]]:
        """获取最近几天的新闻"""
        recent_news = []
        threshold_date = datetime.now() - timedelta(days=days)
        
        # 遍历新闻文件
        for filename in os.listdir(self.news_dir):
            if filename.endswith('.json'):
                try:
                    file_date = datetime.strptime(filename[:-5], '%Y-%m-%d')
                    if file_date >= threshold_date:
                        file_path = os.path.join(self.news_dir, filename)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            news_items = json.load(f)
                            recent_news.extend(news_items)
                except Exception as e:
                    print(f"读取新闻文件失败 {filename}: {e}")
        
        # 去重
        unique_news = self._deduplicate_news(recent_news)
        
        return unique_news
    
    def clean_old_news(self):
        """清理过期的新闻文件"""
        threshold_date = datetime.now() - timedelta(days=settings.NEWS_RETENTION_DAYS)
        
        for filename in os.listdir(self.news_dir):
            if filename.endswith('.json'):
                try:
                    file_date = datetime.strptime(filename[:-5], '%Y-%m-%d')
                    if file_date < threshold_date:
                        file_path = os.path.join(self.news_dir, filename)
                        os.remove(file_path)
                        print(f"删除过期新闻文件: {filename}")
                except Exception as e:
                    print(f"清理新闻文件失败 {filename}: {e}")
    
    def _is_rsshub_url(self, url: str) -> bool:
        """检测URL是否是RSSHub URL"""
        for instance in self.rsshub_instances:
            if instance in url:
                return True
        return False
    
    def _replace_rsshub_instance(self, url: str, new_instance: str) -> str:
        """替换URL中的RSSHub实例"""
        # 移除原有的RSSHub实例前缀
        for instance in self.rsshub_instances:
            if instance in url:
                path = url.replace(instance, '')
                # 确保路径以/开头
                if not path.startswith('/'):
                    path = '/' + path
                # 组合新的URL
                return new_instance + path
        # 如果不是RSSHub URL，直接返回原URL
        return url


if __name__ == "__main__":
    # 测试新闻抓取
    fetcher = NewsFetcher()
    news = fetcher.fetch_news()
    print(f"获取到 {len(news)} 条新闻")
    
    # 清理过期新闻
    fetcher.clean_old_news()
