from ..model import site, SiteAdapterBase
from bs4 import BeautifulSoup
import re

@site([
    r'https?://(www\.)?stackoverflow\.com/questions/\d+',
])
class StackOverflowQuestionAdapter(SiteAdapterBase):
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

        # 提取问题信息
        question = soup.find('div', class_='question')
        if question:
            # 问题内容
            q_content = question.find('div', class_='s-prose')
            if q_content:
                briefs.append(f"问题: {q_content.get_text().strip()}")

            # 问题标签
            tags = question.find_all('a', class_='post-tag')
            if tags:
                briefs.append(f"标签: {', '.join([t.get_text() for t in tags])}")

        # 提取回答
        answers = soup.find_all('div', class_='answer')
        for i, answer in enumerate(answers[:3]):  # 只取前3个回答
            score = answer.find('div', class_='js-vote-count')
            score_text = f"[得分:{score.get_text()}] " if score else ""
            
            content = answer.find('div', class_='s-prose')
            if content:
                text = content.get_text().strip()
                briefs.append(f"回答{i+1} {score_text}: {text[:500]}...")

        return cls.make_ret(
            status_code=status_code,
            message="ok",
            title=title,
            briefs=briefs
        ) 