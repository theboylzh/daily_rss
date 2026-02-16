import os
import json
import feedparser
from typing import List, Dict, Any
from config import settings


class SubscriptionManager:
    def __init__(self):
        self.subscription_file = os.path.join(settings.DATA_DIR, settings.SUBSCRIPTION_FILE)
        self.opml_file = os.path.join(settings.DATA_DIR, settings.OPML_FILE)
        self.subscriptions = self._load_subscriptions()
    
    def _load_subscriptions(self) -> List[Dict[str, Any]]:
        """加载订阅源列表"""
        # 从配置文件加载当前订阅源
        config_subscriptions = []
        for url in settings.SUBSCRIPTIONS:
            config_subscriptions.append({
                "id": self._generate_id(url),
                "name": url,
                "url": url,
                "type": "rss",
                "last_updated": None
            })
        
        # 尝试从OPML加载
        opml_subscriptions = []
        if os.path.exists(self.opml_file):
            opml_subscriptions = self._parse_opml()
        
        # 合并订阅源
        all_subscriptions = config_subscriptions + opml_subscriptions
        
        # 去重
        seen_urls = set()
        unique_subscriptions = []
        for sub in all_subscriptions:
            if sub["url"] not in seen_urls:
                seen_urls.add(sub["url"])
                unique_subscriptions.append(sub)
        
        # 检查缓存文件是否存在且需要更新
        if os.path.exists(self.subscription_file):
            try:
                with open(self.subscription_file, 'r', encoding='utf-8') as f:
                    cached_subscriptions = json.load(f)
                
                # 比较缓存的订阅源和当前的订阅源
                cached_urls = {sub["url"] for sub in cached_subscriptions}
                current_urls = {sub["url"] for sub in unique_subscriptions}
                
                # 如果订阅源发生变化，更新缓存
                if cached_urls != current_urls:
                    print("订阅源配置发生变化，更新缓存...")
                    # 保留已有的last_updated信息
                    url_to_timestamp = {sub["url"]: sub.get("last_updated") for sub in cached_subscriptions}
                    for sub in unique_subscriptions:
                        if sub["url"] in url_to_timestamp:
                            sub["last_updated"] = url_to_timestamp[sub["url"]]
                    self._save_subscriptions(unique_subscriptions)
                    return unique_subscriptions
                else:
                    # 订阅源未变化，返回缓存的订阅源
                    return cached_subscriptions
            except Exception as e:
                print(f"加载订阅源失败: {e}")
                # 加载失败时使用当前配置
                self._save_subscriptions(unique_subscriptions)
                return unique_subscriptions
        else:
            # 缓存文件不存在，保存并返回当前配置
            self._save_subscriptions(unique_subscriptions)
            return unique_subscriptions
    
    def _save_subscriptions(self, subscriptions: List[Dict[str, Any]]):
        """保存订阅源列表"""
        os.makedirs(os.path.dirname(self.subscription_file), exist_ok=True)
        with open(self.subscription_file, 'w', encoding='utf-8') as f:
            json.dump(subscriptions, f, ensure_ascii=False, indent=2)
    
    def _parse_opml(self) -> List[Dict[str, Any]]:
        """解析OPML文档"""
        try:
            with open(self.opml_file, 'r', encoding='utf-8') as f:
                opml_content = f.read()
            
            parsed = feedparser.parse(opml_content)
            subscriptions = []
            
            for outline in parsed.get('items', []):
                if 'xmlUrl' in outline:
                    subscriptions.append({
                        "id": self._generate_id(outline['xmlUrl']),
                        "name": outline.get('title', outline['xmlUrl']),
                        "url": outline['xmlUrl'],
                        "type": "rss",
                        "last_updated": None
                    })
            
            return subscriptions
        except Exception as e:
            print(f"解析OPML失败: {e}")
            return []
    
    def _generate_id(self, url: str) -> str:
        """根据URL生成唯一ID"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()
    
    def add_subscription(self, url: str, name: str = None):
        """添加订阅源"""
        # 检查是否已存在
        for sub in self.subscriptions:
            if sub["url"] == url:
                print(f"订阅源已存在: {url}")
                return False
        
        # 添加新订阅源
        new_subscription = {
            "id": self._generate_id(url),
            "name": name or url,
            "url": url,
            "type": "rss",
            "last_updated": None
        }
        
        self.subscriptions.append(new_subscription)
        self._save_subscriptions(self.subscriptions)
        print(f"添加订阅源成功: {url}")
        return True
    
    def remove_subscription(self, subscription_id: str):
        """删除订阅源"""
        original_length = len(self.subscriptions)
        self.subscriptions = [sub for sub in self.subscriptions if sub["id"] != subscription_id]
        
        if len(self.subscriptions) < original_length:
            self._save_subscriptions(self.subscriptions)
            print(f"删除订阅源成功: {subscription_id}")
            return True
        else:
            print(f"订阅源不存在: {subscription_id}")
            return False
    
    def get_subscriptions(self) -> List[Dict[str, Any]]:
        """获取所有订阅源"""
        return self.subscriptions
    
    def update_subscription_timestamp(self, subscription_id: str, timestamp: str):
        """更新订阅源的最后更新时间"""
        for sub in self.subscriptions:
            if sub["id"] == subscription_id:
                sub["last_updated"] = timestamp
                self._save_subscriptions(self.subscriptions)
                break


if __name__ == "__main__":
    # 测试订阅源管理
    manager = SubscriptionManager()
    print("当前订阅源:")
    for sub in manager.get_subscriptions():
        print(f"- {sub['name']}: {sub['url']}")
    
    # 测试添加订阅源
    # manager.add_subscription("https://example.com/rss", "Example RSS")
    
    # 测试删除订阅源
    # if manager.get_subscriptions():
    #     manager.remove_subscription(manager.get_subscriptions()[0]['id'])
