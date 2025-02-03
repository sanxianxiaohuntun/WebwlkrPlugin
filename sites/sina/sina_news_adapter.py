from ..model import site, SiteAdapterBase
from bs4 import BeautifulSoup
import re

@site([
    r'https?://news\.sina\.com\.cn/[a-z]/[0-9-]+/doc-[a-zA-Z0-9]+\.shtml',
])
class SinaNewsAdapter(SiteAdapterBase):
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
        briefs = cls.regexp_brief(raw_html, "标题", r'<h1[^>]*class="main-title"[^>]*>(.*?)</h1>', briefs)
        briefs = cls.regexp_brief(raw_html, "来源", r'<span[^>]*class="source"[^>]*>(.*?)</span>', briefs)
        briefs = cls.regexp_brief(raw_html, "发布时间", r'<span[^>]*class="date"[^>]*>(.*?)</span>', briefs)
        
        # 提取新闻正文
        article = soup.find('div', class_='article')
        if article:
            # 去除广告等无关内容
            for ad in article.find_all(['div', 'script'], class_=['recommend', 'statement', 'article-footer']):
                ad.decompose()
            content = article.get_text().strip()
            briefs.append(f"正文: {content[:brief_len]}...")

        return cls.make_ret(
            status_code=status_code,
            message="ok",
            title=title,
            briefs=briefs
        ) 