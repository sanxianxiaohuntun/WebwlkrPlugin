from ..model import site, SiteAdapterBase
from bs4 import BeautifulSoup
import re

@site([
    r'https?://(www\.)?bilibili\.com/video/[A-Za-z0-9]+',
])
class BilibiliVideoAdapter(SiteAdapterBase):
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

        # 提取视频信息
        briefs = cls.regexp_brief(raw_html, "Title", r'<h1[^>]*title="([^"]+)"', briefs)
        briefs = cls.regexp_brief(raw_html, "UP主", r'<a[^>]*class="[^"]*up-name[^"]*"[^>]*>([^<]+)</a>', briefs)
        briefs = cls.regexp_brief(raw_html, "播放量", r'<span[^>]*class="[^"]*view[^"]*"[^>]*>([^<]+)</span>', briefs)
        briefs = cls.regexp_brief(raw_html, "简介", r'<div[^>]*class="[^"]*desc-info[^"]*"[^>]*>(.*?)</div>', briefs)

        return cls.make_ret(
            status_code=status_code,
            message="ok",
            title=title,
            briefs=briefs
        ) 