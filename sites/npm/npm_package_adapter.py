from ..model import site, SiteAdapterBase
from bs4 import BeautifulSoup
import re

@site([
    r'https?://(www\.)?npmjs\.com/package/[@a-zA-Z0-9-_/]+',
])
class NPMPackageAdapter(SiteAdapterBase):
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

        # 提取包信息
        briefs = cls.regexp_brief(raw_html, "包名", r'<h2[^>]*class="[^"]*package-name[^"]*"[^>]*>(.*?)</h2>', briefs)
        briefs = cls.regexp_brief(raw_html, "版本", r'<p[^>]*class="[^"]*package-description[^"]*"[^>]*>(.*?)</p>', briefs)
        briefs = cls.regexp_brief(raw_html, "周下载量", r'<span[^>]*class="[^"]*weekly-downloads[^"]*"[^>]*>(.*?)</span>', briefs)

        # 提取README内容
        readme = soup.find('div', id='readme')
        if readme:
            content = readme.get_text().strip()
            briefs.append(f"README: {content[:brief_len]}...")

        return cls.make_ret(
            status_code=status_code,
            message="ok",
            title=title,
            briefs=briefs
        ) 