import re
import logging
import time
import yaml

from .sites import model
from .cache import Cache

# 读取配置
try:
    with open("webwlkr.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
except Exception as e:
    logging.error(f"Failed to load config: {e}")
    config = {}

# 创建缓存实例，使用默认值
cache = Cache(
    expire_time=config.get('cache', {}).get('expire_time', 300),
    max_size=config.get('cache', {}).get('max_size', 1000)
)

def process(url: str, brief_len: int, **kwargs) -> str:
    """处理网页内容"""
    # 检查缓存配置是否启用
    if config.get('cache', {}).get('enabled', True):
        cached = cache.get(url)
        if cached:
            return cached

    adapter_cls: model.SiteAdapterBase = model.SiteAdapterBase

    found = False
    for adapter in model.__site_adapters__:
        for regexp in adapter['regexp']:
            if re.match(regexp, url):
                if not adapter['cls'].feed(url):
                    # 匹中了这个适配器，但适配器不接受这个链接
                    # 则直接检查下一个适配器
                    break
                adapter_cls = adapter['cls']
                found = True
                break
        if found:
            break

    logging.debug("site adapter: {}".format(adapter_cls))

    processed: dict = adapter_cls.process(url, brief_len, **kwargs)

    logging.debug("site adapter ret: {}".format(processed))

    # 处理成纯文本

    text: str = ""

    if processed.get('status', 200) == 200:
        if 'content' not in processed:
            text = processed.get('message', "nothing found")
        else:
            text += ('title: '+processed['content']['title']+"\n") if 'title' in processed['content'] else ''
            text += '\n'.join(processed['content'].get('briefs', []))
    else:
        raise Exception(processed.get('message', "error"))

    # 存入缓存
    if config.get('cache', {}).get('enabled', True):
        cache.set(url, text)
        
    return text