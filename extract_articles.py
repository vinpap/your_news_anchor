"""
This script extracts and filters news articles from a list of RSS feeds and 
saves them using a provided API.
"""
import logging

import requests
import feedparser
import newspaper
import yaml


def parse_rss_feed(source_id: int, source_name: str, feed_path: str, articles_max_count=10) -> list:
    """
    Retrieves the RSS feed located at feed_path and returns a dictionary that
    contains the n first articles along with their URL and their title.

    feed_path: path to the RSS feed to process
    articles_max_count: how many articles should be extracted from the RSS, at
    most.

    Returns a list of dictionaries that include the following elements:
    'title': title of the article
    'content': content of the article
    'source': the name of the website the news originate from (equal to 
    'source_name')
    'url': the URL where the article can be found.
    """
    articles = []

    news_feed = feedparser.parse(feed_path) # Parsing the RSS feed
    scraped_articles = 0
    for item in news_feed.entries:
        article_data = {
            "title": item.title,
            "url": item.link,
            "source": source_name,
            "source_id": source_id
        }
        try:
            article_data["content"] = parse_article_webpage(item.link)
            if not content_is_relevant(article_data["content"]):
                continue
        except newspaper.article.ArticleException:
            continue

        articles.append(article_data)
        scraped_articles += 1
        if scraped_articles >= articles_max_count:
            break
        
    return articles

def parse_article_webpage(url: str) -> str:
    """
    Parses a webpage and returns the text content of the news article found on it.
    """
    article = newspaper.Article(url)
    article.download()
    article.parse()

    return article.text

def content_is_relevant(article: str) -> bool:
    """
    Checks the content of a news article to make sure it is relevant and can be
    used to generate a recap.

    More specifically, this function aims to filter out these kinds of content:
    - Video reports, where the actual news content is presented in a video and
    the text content only serves as a caption.
    - Ads that were improperly detected as news articles by newspaper.Article
    - Articles that are too short too extract any meaningful recaps, such as 
    live newsfeeds content for example.

    Returns a boolean (True -> the content can be used, False -> it can't).
    """

    # Articles too short are deleted as they cannot be used efficiently.
    # These might be video articles, ads, short articles, or articles that
    # were not properly processed by newspaper.Article.
    if len(article) < 500:
        return False
    
    return True

    # Ajouter un moyen de filtrer les articles réservés aux abonnés, si nécessaire


def get_sources_list(endpoint: str) -> list:
    """
    Returns the list of RSS feeds to get articles from in the database.
    """
    logging.getLogger().info("Retrieving RSS feeds list from API endpoint")
    sources = requests.get(endpoint)
    return sources.json()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    logger = logging.getLogger()
    logger.info("Starting news articles extraction...")
    config = yaml.safe_load(open("./config.yml"))

    logger.info(f"""Database API endpoint: {config["api"]}""")
    logger.info(f"""Max number of articles to scrap per source: {config["max_articles_per_source"]}""")

    # Retrieving the list of RSS feeds from the API
    rss_sources = get_sources_list(config["api"] + "/feeds")

    scraped_articles = []

    for source in rss_sources:
        logger.info(f"""Extracting articles from RSS feed {source["url"]}""")
        results = parse_rss_feed(source_id=source["source_id"], source_name=source["name"], feed_path=source["url"], articles_max_count=config["max_articles_per_source"])
        scraped_articles.extend(results)
    
    logger.info("Articles extraction complete!")

    logger.info("Saving all articles...")
    response = requests.post(config["api"] + "/update_articles", json={"articles": scraped_articles, "security_token": config["security_token"]})
    if response.status_code != 200:
        logger.error(f"Update of daily articles failed. Response: {response.text}")
    else:
        logger.info("Save complete!")

