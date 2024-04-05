"""
Vincent Papelard, 2024

This script extracts and filters news articles from a list of RSS feeds and 
saves them using a provided API. It is meant to be run at regular intervals, 
e.g. once per day, so that the saved news articles stay up-to-date.
"""

import os
import logging

import requests

from extraction_functions import parse_rss_feed, get_sources_list


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger()
    logger.info("Starting news articles extraction...")
    config = {}

    # Getting API key and endpoint from environment values
    config["security_token"] = os.environ["API_TOKEN"]
    config["API"] = os.environ["API"]
    config["max_articles_per_source"] = 5

    logger.info(f"""Database API endpoint: {config["API"]}""")
    logger.info(
        f"""Max number of articles to scrap per source: {config["max_articles_per_source"]}"""
    )

    # Retrieving the list of RSS feeds from the API
    rss_sources = get_sources_list(config["API"] + "/all_feeds")
    
    print(rss_sources)

    scraped_articles = []

    for source in rss_sources:
        logger.info(f"""Extracting articles from RSS feed {source["url"]}""")
        results = parse_rss_feed(
            source_id=source["source_id"],
            source_name=source["name"],
            feed_path=source["url"],
            articles_max_count=config["max_articles_per_source"],
            is_from_user=source["is_from_user"],
        )
        scraped_articles.extend(results)

    logger.info("Articles extraction complete!")

    logger.info("Saving all articles...")
    response = requests.post(
        config["API"] + "/update_articles",
        json={"articles": scraped_articles, "security_token": config["security_token"]},
    )
    if response.status_code != 200:
        logger.error(f"Update of daily articles failed. Response: {response.text}")
    else:
        logger.info("Save complete!")
