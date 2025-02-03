from ..model import site, SiteAdapterBase
from bs4 import BeautifulSoup
import re

@site([
    r'https?://new\.qq\.com/[a-z]+/[0-9A-Z]{16}',
    r'https?://new\.qq\.com/rain/a/[0-9A-Z]{16}',
])
class QQNewsAdapter(SiteAdapterBase):
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
        briefs = cls.regexp_brief(raw_html, "标题", r'<h1[^>]*class="title"[^>]*>(.*?)</h1>', briefs)
        briefs = cls.regexp_brief(raw_html, "来源", r'<div[^>]*class="src"[^>]*>(.*?)</div>', briefs)
        briefs = cls.regexp_brief(raw_html, "发布时间", r'<div[^>]*class="time"[^>]*>(.*?)</div>', briefs)
        
        # 提取新闻正文
        article = soup.find('div', class_='content-article')
        if article:
            # 去除视频、广告等
            for elem in article.find_all(['div', 'script'], class_=['rv-player', 'cm-banner']):
                elem.decompose()
            content = article.get_text().strip()
            briefs.append(f"正文: {content[:brief_len]}...")

        return cls.make_ret(
            status_code=status_code,
            message="ok",
            title=title,
            briefs=briefs
        ) 