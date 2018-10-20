from wiki.models import WikiArticle


def test_get_all_articles(client):
    articles = WikiArticle.get_all()
    assert len(articles) == 3
