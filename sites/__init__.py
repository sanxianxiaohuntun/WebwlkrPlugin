# 导入所有站点适配器
from .github.github_repo_adapter import GithubRepoSiteAdapter
from .github.github_user_adapter import GithubUserSiteAdapter
from .bilibili.bilibili_video_adapter import BilibiliVideoAdapter
from .bilibili.bilibili_article_adapter import BilibiliArticleAdapter
from .stackoverflow.stackoverflow_question_adapter import StackOverflowQuestionAdapter
from .bbc.bbc_news_adapter import BBCNewsAdapter
from .youtube.youtube_video_adapter import YouTubeVideoAdapter

__all__ = [
    'GithubRepoSiteAdapter',
    'GithubUserSiteAdapter',
    'BilibiliVideoAdapter',
    'BilibiliArticleAdapter',
    'StackOverflowQuestionAdapter',
    'BBCNewsAdapter',
    'YouTubeVideoAdapter'
]
