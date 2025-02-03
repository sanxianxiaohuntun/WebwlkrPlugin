from ..model import site, SiteAdapterBase
from bs4 import BeautifulSoup
import re

@site([
    r'https?://(www\.)?bbc\.(com|co\.uk)/news/[a-zA-Z0-9-]+',
])
class BBCNewsAdapter(SiteAdapterBase):
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
        briefs = cls.regexp_brief(raw_html, "标题", r'<h1[^>]*class="[^"]*story-body__h1[^"]*"[^>]*>(.*?)</h1>', briefs)
        briefs = cls.regexp_brief(raw_html, "时间", r'<div[^>]*class="[^"]*date[^"]*"[^>]*data-datetime="([^"]+)"', briefs)
        
        # 提取新闻导语
        intro = soup.find('div', class_='story-body__introduction')
        if intro:
            briefs.append(f"导语: {intro.get_text().strip()}")
        
        # 提取新闻正文
        article = soup.find('div', class_='story-body__inner')
        if article:
            # 去除相关链接、广告等
            for elem in article.find_all(['div', 'figure'], class_=['related-links', 'ad-slot']):
                elem.decompose()
            content = article.get_text().strip()
            briefs.append(f"正文: {content[:brief_len]}...")

        return cls.make_ret(
            status_code=status_code,
            message="ok",
            title=title,
            briefs=briefs
        ) 