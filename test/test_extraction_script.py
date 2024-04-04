"""
Vincent Papelard, 2024

Testing script for extract_articles.py.
"""

import newspaper
import extraction_functions


def test_article_page_parsing():
    """
    Makes sure that parse_article_page returns a dictionary that follows the
    proper format.
    """

    url = "https://www.lemonde.fr/societe/article/2024/01/19/proces-de-l-affaire-theo-les-trois-policiers-fixes-sur-leur-sort-vendredi_6211768_3224.html"
    try:
        article = extraction_functions.parse_article_webpage(url)
        assert isinstance(article, dict)
        assert list(article.keys()) == ["text", "authors", "date", "image"]
    except newspaper.article.ArticleException:
        print(f"Unable to retrieve article from URL {url}")
        print(
            "test_article_page_parsing could not be run as a result. Please use another URL"
        )


def test_author_filtering():
    """
    Checks the return value of filter_authors to make sure it only kept authors
    name refering to people.
    """
    authors_list = ["Jean-Jacques Dupont", "Par", "Vidéo", "Article", "Jeanne Durand"]
    assert extraction_functions.filter_authors(authors_list) == [
        "Jean-Jacques Dupont",
        "Jeanne Durand",
    ]


def test_content_is_relevant():
    """
    Checks if content_is_relevant filters out text content that is too short.
    """

    irrelevant_text = "Subscribe to our great newsletter for $10/month only!"
    irrelevant_text_2 = "Se connecter"

    assert not extraction_functions.content_is_relevant(irrelevant_text)
    assert not extraction_functions.content_is_relevant(irrelevant_text_2)

    with open("./testing_data/article_example.txt", "r") as article:
        relevant_text = article.read()
        assert extraction_functions.content_is_relevant(relevant_text)
