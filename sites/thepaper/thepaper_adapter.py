from ..model import site, SiteAdapterBase
from bs4 import BeautifulSoup
import re

@site([
    r'https?://(www\.)?thepaper\.cn/newsDetail_forward_\d+',
])
class ThePaperAdapter(SiteAdapterBase):
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

        # 提取新闻信息
        briefs = cls.regexp_brief(raw_html, "标题", r'<h1[^>]*class="news_title"[^>]*>(.*?)</h1>', briefs)
        briefs = cls.regexp_brief(raw_html, "来源", r'<div[^>]*class="news_about"[^>]*>(.*?)</div>', briefs)
        briefs = cls.regexp_brief(raw_html, "发布时间", r'<div[^>]*class="news_time"[^>]*>(.*?)</div>', briefs)
        
        # 提取新闻正文
        article = soup.find('div', class_='news_txt')
        if article:
            # 去除图片说明等
            for caption in article.find_all('figcaption'):
                caption.decompose()
            content = article.get_text().strip()
            briefs.append(f"正文: {content[:brief_len]}...")

        return cls.make_ret(
            status_code=status_code,
            message="ok",
            title=title,
            briefs=briefs
        ) 