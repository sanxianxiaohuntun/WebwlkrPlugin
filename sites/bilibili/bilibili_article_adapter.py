from ..model import site, SiteAdapterBase
from bs4 import BeautifulSoup
import re

@site([
    r'https?://(www\.)?bilibili\.com/read/cv\d+',
])
class BilibiliArticleAdapter(SiteAdapterBase):
    @classmethod
    def process(cls, url: str, brief_len: int, **kwargs) -> dict:
        status_code, raw_html = cls.get_html(url)
        if status_code != 200:
            return cls.make_ret(
                status_code=status_code,
                message="error"
            )

        soup = BeautifulSoup(raw_html, 'html.parser')
        title = soup.title.string
        briefs = []

        # 提取文章信息
        briefs = cls.regexp_brief(raw_html, "标题", r'<h1[^>]*class="title"[^>]*>(.*?)</h1>', briefs)
        briefs = cls.regexp_brief(raw_html, "作者", r'<a[^>]*class="[^"]*author-name[^"]*"[^>]*>(.*?)</a>', briefs)
        briefs = cls.regexp_brief(raw_html, "阅读量", r'<span[^>]*class="view"[^>]*>(.*?)</span>', briefs)
        
        # 提取文章内容
        article = soup.find('div', class_='article-holder')
        if article:
            content = article.get_text().strip()
            briefs.append(f"内容: {content[:brief_len]}...")

        return cls.make_ret(
            status_code=status_code,
            message="ok",
            title=title,
            briefs=briefs
        ) 