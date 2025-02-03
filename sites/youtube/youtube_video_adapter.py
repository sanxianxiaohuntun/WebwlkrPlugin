from ..model import site, SiteAdapterBase
from bs4 import BeautifulSoup
import re

@site([
    r'https?://(www\.)?youtube\.com/watch\?v=[a-zA-Z0-9_-]+',
    r'https?://youtu\.be/[a-zA-Z0-9_-]+',
])
class YouTubeVideoAdapter(SiteAdapterBase):
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
        briefs = cls.regexp_brief(raw_html, "标题", r'"title":"([^"]+)"', briefs)
        briefs = cls.regexp_brief(raw_html, "作者", r'"author":"([^"]+)"', briefs)
        briefs = cls.regexp_brief(raw_html, "观看次数", r'"viewCount":"(\d+)"', briefs)
        briefs = cls.regexp_brief(raw_html, "上传时间", r'"uploadDate":"([^"]+)"', briefs)
        
        # 提取视频描述
        description = soup.find('meta', {'name': 'description'})
        if description and description.get('content'):
            content = description['content'].strip()
            briefs.append(f"描述: {content[:brief_len]}...")

        return cls.make_ret(
            status_code=status_code,
            message="ok",
            title=title,
            briefs=briefs
        ) 