from ..model import site, SiteAdapterBase

from bs4 import BeautifulSoup

import re

# 匹配大于两层的路径
@site([
    r'https?://github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)',
    r'https?://www\.github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)',
])
class GithubRepoSiteAdapter(SiteAdapterBase):

    @classmethod
    def feed(cls, url: str) -> bool:
        """判断是否适配此网址"""
        return True

    @classmethod
    def process(cls, url: str, brief_len: int, **kwargs) -> dict:
        """处理网页内容"""
        status_code, raw_html = cls.get_html(url)
        if status_code != 200:
            return cls.make_ret(
                status_code=status_code,
                message="error"
            )

        soup = BeautifulSoup(raw_html, 'html.parser')
        title = soup.title.string

        briefs = []

        raw = soup.get_text()

        # strip每一行
        raw = '\n'.join([line.strip() for line in raw.split('\n')])

        # 删除所有空行或只有空格的行
        raw = re.sub(r'\n\s*\n', '\n', raw)

        delete = """Actions
        Automate any workflow
        Packages
        Host and manage packages
        Security
        Find and fix vulnerabilities
        Codespaces
        Instant dev environments
        Copilot
        Write better code with AI
        Code review
        Manage code changes
        Issues
        Plan and track work
        Discussions
        Collaborate outside of code
        Explore
        All features
        Documentation
        GitHub Skills
        Blog
        Solutions
        For
        Enterprise
        Teams
        Startups
        Education
        By Solution
        CI/CD & Automation"""

        raw = re.sub(delete, '', raw)

        briefs.append("brief raw: "+raw)

        # 提取仓库基本信息
        briefs = cls.regexp_brief(raw_html, "Stars", r'aria-label="([\d,]+) users starred this repository"', briefs)
        briefs = cls.regexp_brief(raw_html, "Forks", r'aria-label="([\d,]+) users forked this repository"', briefs)
        briefs = cls.regexp_brief(raw_html, "Description", r'<p class="f4 my-3">(.*?)</p>', briefs)
        
        # 提取README内容
        briefs = cls.regexp_brief(raw_html, "README", r'<article class="markdown-body.*?">(.*?)</article>', briefs)

        return cls.make_ret(
            status_code=status_code,
            message="ok",
            title=title,
            briefs=briefs
        )