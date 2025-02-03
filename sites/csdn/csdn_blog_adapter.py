from ..model import site, SiteAdapterBase
from bs4 import BeautifulSoup
import re

@site([
    r'https?://blog\.csdn\.net/[^/]+/article/details/\d+',
])
class CSDNBlogAdapter(SiteAdapterBase):
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
        briefs = cls.regexp_brief(raw_html, "标题", r'<h1[^>]*class="title-article"[^>]*>(.*?)</h1>', briefs)
        briefs = cls.regexp_brief(raw_html, "作者", r'<a[^>]*class="follow-nickName"[^>]*>(.*?)</a>', briefs)
        briefs = cls.regexp_brief(raw_html, "阅读量", r'<span[^>]*class="read-count"[^>]*>(.*?)</span>', briefs)
        
        # 提取文章内容
        article = soup.find('div', id='article_content')
        if article:
            content = article.get_text().strip()
            briefs.append(f"内容: {content[:brief_len]}...")

        return cls.make_ret(
            status_code=status_code,
            message="ok",
            title=title,
            briefs=briefs
        ) 