import os
import logging

import feedparser
import newspaper
import requests

# Spacy's named entity detection is used to filter the authors' names by keeping
# people's name only
import spacy

nlp = spacy.load("fr_core_news_lg")


def parse_rss_feed(
    source_id: int,
    source_name: str,
    feed_path: str,
    articles_max_count=10,
    is_from_user=False,
) -> list:
    """
    Retrieves the RSS feed located at feed_path and returns a dictionary that
    contains the n first articles along with their URL and their title.

    feed_path: path to the RSS feed to process
    - source_id: the id that points to the RSS feed in the database. Retrieved
    from the API (cf get_sources_list)
    - source_name: the RSS source name, also retrieved from the API
    - feed_path: the URL (or filepath) to the RSS feed
    - articles_max_count: the max number of articles to extract from the RSS
    feed. This function will extract the articles content in their order in the
    RSS feed, until 'articles_max_count' articles have been extracted or the end
    of the feed has been reached.
    - is_from_user: whether the news source has been added by an user or is a standard one

    Returns a list of dictionaries that include the following elements:
    - 'title': title of the article
    - 'content': content of the article
    - 'source': the name of the website the news originate from (equal to
    'source_name')
    - 'source_id': the unique ID given to the source, as provided by the
    'source_id' parameter
    - 'url': the URL where the article can be found.
    """
    articles = []

    news_feed = feedparser.parse(feed_path)  # Parsing the RSS feed
    scraped_articles = 0
    for item in news_feed.entries:
        article_data = {
            "title": item.title,
            "url": item.link,
            "source": source_name,
            "source_id": source_id,
            "is_from_user": is_from_user,
        }
        try:
            parsed_article = parse_article_webpage(item.link)

            # The function call below makes sure that the article content
            # is relevant and can be used, cf function docstring for further
            # info
            if not content_is_relevant(parsed_article["text"]):
                # Irrelevant entries in the RSS feed are simply ignored
                continue

            article_data["content"] = parsed_article["text"]

            # Authors name are filtered in order to get rid of some bad
            # detections, e.g. errors caused by an improper use of capital
            # letters or point
            article_data["authors"] = parsed_article["authors"]
            article_data["authors"] = filter_authors(article_data["authors"])
            article_data["authors"] = ", ".join(article_data["authors"])

            article_data["date"] = parsed_article["date"]
            article_data["image"] = parsed_article["image"]

        except newspaper.article.ArticleException:
            continue

        articles.append(article_data)
        scraped_articles += 1
        if scraped_articles >= articles_max_count:
            break

    return articles


def parse_article_webpage(url: str) -> dict:
    """
    Parses a webpage and returns a dictionary that contains its web content as
    well as some metadata about it.
    """
    article = newspaper.Article(url)
    article.download()
    article.parse()
    response_object = {
        "text": article.text,
        "authors": article.authors,
    }
    try:
        response_object["date"] = article.publish_date.strftime("%a %d %b %Y, %I:%M%p")
    # Accounting for the case where no date was found
    except AttributeError:
        response_object["date"] = ""

    try:
        response_object["image"] = article.top_image
    # In case no image was found
    except:
        response_object["image"] = ""

    return response_object


def filter_authors(authors: list) -> list:
    """
    Filters the authors for an article in order to get rid of errors during
    authors detection.

    In order to do that, named-entity detection (NER) is run on the list of
    authors. Only those that are identified as refering to a person are kept.
    """

    filtered_authors = []
    entities = nlp(", ".join(authors))
    for word in entities.ents:
        if word.label_ == "PER":
            filtered_authors.append(word.text)

    return filtered_authors


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
    - Website banners prompting the reader to subscribe to the newspaper, which
    are sometimes improperly detected as article content.

    Returns a boolean (True -> the content can be used, False -> it can't).
    """

    # Articles too short are deleted as they cannot be used efficiently.
    # These might be video articles, ads, short articles, or articles that
    # were not properly processed by newspaper.Article.
    if len(article) < 500:
        return False

    return True


def get_sources_list(endpoint: str) -> list:
    """
    Returns the list of RSS feeds to get articles from in the database.
    """
    logging.getLogger().info("Retrieving RSS feeds list from API endpoint")
    sources = requests.post(endpoint, params={"secret_token": os.environ["API_TOKEN"]})
    return sources.json()
