from algo.config import settings
from algo.pipeline import FactChecker


checker = FactChecker(settings)


def check_article(article: str):
    return checker.check_article(article)
