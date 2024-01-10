"""
Ce script doit être exécuté à intervalles réguliers. Les articles extraits doivent
être insérés dans la base de données déployée sur Azure.
"""

import feedparser
from newspaper import Article

def parse_rss_feed(feed_path: str, articles_max_count=10) -> list:
    """
    Retrieves the RSS feed located at feed_path and returns a dictionary that
    contains the n first articles along with their URL and their title.

    feed_path: path to the RSS feed to process
    articles_max_count: how many articles should be extracted from the RSS, at
    most.

    Returns a list of dictionaries that include the following elements:
    'title': title of the article
    'content': content of the article
    'url': the URL where the article can be found.
    """
    articles = []

    news_feed = feedparser.parse(feed_path) # Parsing the RSS feed
    for index, item in enumerate(news_feed.entries):
        if index >= articles_max_count:
            break
        article_data = {
            "title": item.title,
            "url": item.link,
            "content": parse_article_webpage(item.link)
        }
        articles.append(article_data)
        
    return articles

def parse_article_webpage(url: str) -> str:
    """
    Parses a webpage and returns the text content of the news article found on it.
    """
    article = Article(url)
    article.download()
    article.parse()

    return article.text