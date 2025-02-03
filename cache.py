import time
from collections import OrderedDict
import threading

class Cache:
    def __init__(self, expire_time=300, max_size=1000):
        self.cache = OrderedDict()  # 使用OrderedDict来实现LRU缓存
        self.expire_time = expire_time
        self.max_size = max_size
        self.lock = threading.Lock()  # 添加线程锁保证线程安全
        
    def get(self, url):
        with self.lock:
            if url in self.cache:
                data, timestamp = self.cache[url]
                if time.time() - timestamp < self.expire_time:
                    # 移动到最新
                    self.cache.move_to_end(url)
                    return data
                else:
                    # 过期删除
                    del self.cache[url]
            return None
        
    def set(self, url, data):
        with self.lock:
            # 检查容量
            if len(self.cache) >= self.max_size:
                # 删除最旧的
                self.cache.popitem(last=False)
            self.cache[url] = (data, time.time())
            
    def clear_expired(self):
        """清理过期缓存"""
        with self.lock:
            current_time = time.time()
            expired_keys = [
                k for k, (_, t) in self.cache.items() 
                if current_time - t >= self.expire_time
            ]
            for k in expired_keys:
                del self.cache[k] 