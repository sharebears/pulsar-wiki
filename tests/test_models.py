import pytest

from conftest import check_dictionary
from core import NewJSONEncoder
from core.exceptions import APIException
from wiki.models import (
    WikiAlias,
    WikiArticle,
    WikiLanguage,
    WikiRevision,
    WikiTranslation,
)


def test_get_all_articles(client):
    articles = WikiArticle.get_all()
    assert len(articles) == 3
    assert 4 not in {a.id for a in articles}


def test_get_article_properties(client):
    article = WikiArticle.from_pk(1)
    assert len(article.languages) == 3
    assert all(l.language in {'en', 'es', 'fr'} for l in article.languages)
    assert len(article.aliases) == 4
    assert all(
        a in {'wiki1', 'wikiuno', 'wikione', 'diddles1'}
        for a in article.aliases
    )
    assert article.latest_revision.revision_id == 2


def test_last_revision_other(client):
    article = WikiArticle.from_pk(2)
    assert article.latest_revision.revision_id == 1


def test_get_all_articles_include_dead(client):
    articles = WikiArticle.get_all(include_dead=True)
    assert len(articles) == 4


def test_new_wiki_article(client):
    article = WikiArticle.new(
        title='new article', contents='new article contents', user_id=1
    )
    assert article.id == 5
    assert article.aliases == ['newarticle']
    assert article.latest_revision.title == 'new article'
    assert article.latest_revision.contents == 'new article contents'


def test_new_wiki_article_clashing_name(client):
    with pytest.raises(APIException) as e:
        WikiArticle.new(
            title='Wiki 1', contents='new article contents', user_id=1
        )
    assert e.value.message == 'The wiki alias wiki1 has already been taken.'


def test_translation_new(client):
    translation = WikiTranslation.new(
        article_id=3,
        title='articulo tres',
        language_id=2,
        contents='un articulo nuevo y mi gusta huevos',
        user_id=3,
    )
    assert translation.parent_article.id == 3


def test_translation_new_duplicate_alias(client):
    translation = WikiTranslation.new(
        article_id=3,
        title='wiki      1',
        language_id=2,
        contents='un articulo nuevo y mi gusta huevos',
        user_id=3,
    )
    assert translation.parent_article.id == 3
    assert translation.language.language == 'es'


def test_wiki_revisions_from_article(client):
    revisions = WikiRevision.from_article(article_id=1, language_id=1)
    assert len(revisions) == 2
    assert all(r.article_id == 1 for r in revisions)
    assert all(r.language_id == 1 for r in revisions)
    assert all(r.revision_id in {1, 2} for r in revisions)
    assert all(r.parent_article.id == 1 for r in revisions)


def test_wiki_new_revision(client):
    article = WikiArticle.from_pk(1)
    assert article.latest_revision.revision_id == 2
    assert len(article.aliases) == 4
    assert article.latest_revision.editor.id == 1
    assert article.latest_revision.editor_id == 1
    article.edit(title='new article 1', contents='bump', editor_id=4)
    assert article.title == 'new article 1'
    assert article.contents == 'bump'
    assert article.latest_revision.revision_id == 3
    assert article.latest_revision.editor_id == 4
    assert article.latest_revision.editor.id == 4
    assert len(article.aliases) == 5


def test_new_revision_translation(client):
    translation = WikiTranslation.from_attrs(article_id=1, language_id=2)
    assert translation.latest_revision.revision_id == 1
    assert len(translation.parent_article.aliases) == 4
    translation.edit(title='articulo nuevo 1', contents='bumpo', editor_id=4)
    assert translation.title == 'articulo nuevo 1'
    assert translation.contents == 'bumpo'
    assert translation.latest_revision.revision_id == 2
    assert translation.latest_revision.editor_id == 4
    assert len(translation.parent_article.aliases) == 5


def test_alias_str_to_alias():
    assert WikiAlias.str_to_alias('ab C eeSAjj') == 'abceesajj'


def test_translation_new_invalid_language(client):
    with pytest.raises(APIException) as e:
        WikiLanguage.from_language('af', error=True)
    assert e.value.message == 'Invalid WikiLanguage af.'


def test_translation_valid_language(client):
    assert WikiLanguage.from_language('en', error=True).id == 1


def test_serialize(authed_client):
    article = WikiArticle.from_pk(1)
    data = NewJSONEncoder().default(article)
    check_dictionary(data, {'id': 1, 'title': 'Wiki1'})


def test_serialize_translation(authed_client):
    article = WikiTranslation.from_attrs(article_id=1, language_id=2)
    data = NewJSONEncoder().default(article)
    assert data['title'] == 'WikiUno'
    assert data['language']['id'] == 2
    assert data['parent_article']['id'] == 1
    assert data['latest_revision']['revision_id'] == 1


def test_serialize_revision(authed_client):
    article = WikiRevision.from_attrs(
        revision_id=2, article_id=1, language_id=1
    )
    data = NewJSONEncoder().default(article)
    assert data['title'] == 'Wiki1'
    assert data['language']['id'] == 1
    assert data['parent_article']['id'] == 1
