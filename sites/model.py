import re
import requests
import random
from bs4 import BeautifulSoup
import time
import os


__site_adapters__ = []
"""网站适配器列表
[
    {
        "regexp": [
            "网址正则表达式0",
            "网址正则表达式1",
        ],
        "cls": <SiteAdapterBase>
    }
]
"""

def site(regexp: list[str]):
    """网站适配器装饰器
    """
    def wrapper(cls):
        __site_adapters__.append({
            "regexp": regexp,
            "cls": cls
        })
        return cls
    return wrapper


user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.1.2 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.1 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'
]


class SiteAdapterBase:
    """网站内容适配器的基类"""

    @classmethod
    def feed(cls, url: str) -> bool:
        """判断是否适配此网址"""
        return True

    @classmethod
    def get_html(cls, url: str, timeout: int=10, max_retries=3) -> (int, str):
        """获取网页的HTML内容,支持重试"""
        for i in range(max_retries):
            try:
                proxies = {
                    'http': os.getenv('HTTP_PROXY'),
                    'https': os.getenv('HTTPS_PROXY')
                }
                r = requests.get(
                    url,
                    timeout=timeout,
                    proxies=proxies,
                    headers={
                        'User-Agent': random.choice(user_agents)
                    }
                )
                return r.status_code, r.text
            except Exception as e:
                if i == max_retries - 1:
                    raise e
                time.sleep(1)  # 重试前等待

    @classmethod
    def extra_plain(cls, raw_html: str) -> str:
        """提取网页的纯文本内容"""
        soup = BeautifulSoup(raw_html, 'html.parser')
        raw = soup.get_text()

        # 删除所有空行或只有空格的行
        raw = re.sub(r'\n\s*\n', '\n', raw)

        return raw
    
    @classmethod
    def extra_title_element(cls, raw_html: str) -> str:
        """提取网页的标题元素的纯文字"""
        soup = BeautifulSoup(raw_html, 'html.parser')
        raw = soup.title.string

        return raw

    @classmethod
    def regexp_brief(cls, raw_html: str, key: str, regexp: str, briefs: list[str]) -> list[str]:
        """从网页内容中提取信息，加入到briefs列表中"""

        # 多行匹配
        r = re.compile(regexp, re.DOTALL)

        value = r.search(raw_html)

        # value = re.search(regexp, raw_html)
        if value:
            briefs.append(key+": "+value.group(1).strip())
        return briefs

    @classmethod
    def regexp_delete(cls, raw_text: str, regexp: str) -> str:
        return re.sub(regexp, '', raw_text)

    @classmethod
    def make_ret(
        cls,
        status_code: int=200,
        message: str='ok',
        title: str='',
        briefs: list[str]=[]
    ):
        """生成返回的字典"""
        return {
            "status": status_code,
            "message": message,
            "content": {
                "title": title,
                "briefs": briefs
            }
        }

    @classmethod
    def process(cls, url: str, brief_len: int, **kwargs) -> dict:
        """处理网页内容"""
        status_code, raw_html = cls.get_html(url)
        if status_code != 200:
            return {
                "status": status_code,
                "message": "error status code: "+str(status_code)
            }

        plain = cls.extra_plain(raw_html)
        title = cls.extra_title_element(raw_html)

        if len(plain) >= brief_len:
            plain = plain[:brief_len]

        return {
            "status": status_code,
            "message": "ok",
            "content": {
                "title": title,
                "briefs": [plain]
            }
        }