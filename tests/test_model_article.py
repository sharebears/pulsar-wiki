from wiki.models import WikiArticle
import pytest
from core.exceptions import APIException


def test_get_all_articles(client):
    articles = WikiArticle.get_all()
    assert len(articles) == 3
    assert 4 not in {a.id for a in articles}


def test_get_all_articles_include_dead(client):
    articles = WikiArticle.get_all(include_dead=True)
    assert len(articles) == 4


def test_new_wiki_article(client):
    article = WikiArticle.new(
        title='new article',
        contents='new article contents',
        user_id=1)
    assert article.id == 5
    assert article.aliases == ['newarticle']
    assert article.latest_revision.title == 'new article'
    assert article.latest_revision.contents == 'new article contents'


def test_new_wiki_article_clashing_name(client):
    with pytest.raises(APIException) as e:
        WikiArticle.new(
            title='Wiki 1',
            contents='new article contents',
            user_id=1)
    assert e.value.message == 'The wiki alias wiki1 has already been taken.'
