from datetime import datetime
from typing import List, Optional

import flask
from sqlalchemy import func, and_

from core import cache, db, APIException
from core.mixins import SinglePKMixin, MultiPKMixin
from core.users.models import User
from core.utils import cached_property
from wiki.exceptions import WikiAliasAlreadyExists
from wiki.serializers import WikiRevisionSerializer, WikiArticleSerializer

app = flask.current_app


class WikiArticle(db.Model, SinglePKMixin):
    __tablename__ = 'wiki_articles'
    __cache_key__ = 'wiki_articles_{id}'
    __cache_key_all__ = 'wiki_articles_all'
    __serializer__ = WikiArticleSerializer

    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String(128), nullable=False)
    contents: str = db.Column(db.Text, nullable=False)
    last_updated: datetime = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now())
    deleted: bool = db.Column(db.Boolean, nullable=False, server_default='f', index=True)

    @classmethod
    def get_all(cls, include_dead: bool = False) -> List['WikiArticle']:
        return cls.get_many(
            key=cls.__cache_key_all,
            include_dead=include_dead)

    @classmethod
    def new(cls,
            title: str,
            contents: str,
            user_id: int) -> 'WikiArticle':
        User.is_valid(user_id, error=True)
        cache.delete(cls.__cache_key_all__.format)
        article = super()._new(title=title, contents=contents)
        WikiRevision.new(
            article_id=article.id,
            language_id=1,
            title=title,
            editor_id=user_id,
            contents=contents)
        return article

    @cached_property
    def aliases(self):
        return WikiAliases.from_article(self.id)

    @cached_property
    def latest_revision(self):
        return WikiRevision.latest_revision(self.id)

    @cached_property
    def language(self):
        return WikiLanguage.from_pk(self.language_id)


class WikiTranslation(db.Model, MultiPKMixin):
    __tablename__ = 'wiki_translations'
    __cache_key__ = 'wiki_translations_article_{article_id}_{language_id}'
    __cache_key_from_article__ = 'wiki_translations_of_article_{article_id}'

    article_id: int = db.Column(db.Integer, db.ForeignKey('wiki_articles.id'), primary_key=True)
    language_id: int = db.Column(db.Integer, db.ForeignKey('wiki_languages.id'), primary_key=True)
    title: str = db.Column(db.String(128), nullable=False)
    contents: str = db.Column(db.Text, nullable=False)
    last_updated: datetime = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now())
    deleted: bool = db.Column(db.Boolean, nullable=False, server_default='f', index=True)

    @classmethod
    def from_article(cls, article_id):
        return cls.get_many(
            key=cls.__cache_key_from_article__.format(article_id=article_id),
            filter=cls.article_id == article_id,
            order=cls.language_id.asc())

    @classmethod
    def new(cls,
            article_id: int,
            title: str,
            language: str,
            contents: str,
            user_id: int) -> 'WikiArticle':
        User.is_valid(user_id, error=True)
        language_id = WikiLanguage.from_language(language, error=True)
        cache.delete(cls.__cache_key_all__.format)
        translation = super()._new(
            article_id=article_id,
            language_id=language_id,
            title=title,
            contents=contents,
            author_id=user_id)
        WikiRevision.new(
            article_id=article_id,
            language_id=language_id,
            title=title,
            editor_id=user_id,
            contents=contents)
        return translation

    @cached_property
    def parent_article(self):
        return WikiArticle.from_pk(self.article_id)

    @cached_property
    def language(self):
        return WikiLanguage.from_pk(self.language_id)

    @cached_property
    def latest_revision(self):
        return WikiRevision.latest_revision(self.article_id, self.language_id)


class WikiRevision(db.Model, MultiPKMixin):
    __tablename__ = 'wiki_revisions'
    __cache_key__ = 'wiki_revisions_articles_{article_id}_{revision_id}'
    __cache_key_of_article__ = 'wiki_revisions_of_article_{article_id}'
    __cache_key_latest_id_of_article__ = 'wiki_revisions_latest_{article_id}'
    __serializer__ = WikiRevisionSerializer

    revision_id: int = db.Column(db.Integer, primary_key=True)
    article_id: int = db.Column(db.Integer, db.ForeignKey('wiki_articles.id'), primary_key=True)
    language_id: int = db.Column(db.Integer, db.ForeignKey('wiki_languages.id'), primary_key=True)
    title: str = db.Column(db.String(128), nullable=False)
    editor_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    time_created: datetime = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now())
    contents: str = db.Column(db.Text, nullable=False)

    @classmethod
    def from_article(cls,
                     article_id: int,
                     language_id: int = 1,
                     page: int = 1,
                     limit: int = 50) -> List['WikiRevision']:
        return cls.get_many(
            key=cls.__cache_key_of_article__.format(article_id=article_id),
            filter=and_(cls.article_id == article_id, cls.language_id == language_id),
            order=cls.time_created.desc(),
            page=page,
            limit=limit)

    @classmethod
    def new(cls,
            article_id: int,
            title: str,
            language_id: int,
            editor_id: int,
            contents: str) -> Optional['WikiRevision']:
        WikiArticle.is_valid(article_id, error=True)
        WikiLanguage.is_valid(language_id, error=True)
        old_latest_id = cls.latest_id_from_article(article_id) + 1
        cache.inc(cls.__cache_key_latest_id_of_article__.format(article_id=article_id))
        return super()._new(
            revision_id=old_latest_id,
            article_id=article_id,
            title=title,
            language_id=language_id,
            editor_id=editor_id,
            contents=contents)

    @classmethod
    def latest_revision(cls,
                        article_id: int,
                        language_id: int = 1) -> int:
        cache_key = cls.__cache_key_latest_id_of_article__.format(
            article_id=article_id, language_id=language_id)
        latest_revision_attrs = cache.get(cache_key)
        if latest_revision_attrs:
            return cls.from_attrs(**latest_revision_attrs)
        else:
            latest_revision = (
                cls.query
                .filter(and_(cls.article_id == article_id, cls.language_id == language_id))
                .order_by(cls.revision_id.desc())
                .limit(1))
            cache.set(cache_key, {'article_id': latest_revision.article_id,
                                  'revision_id': latest_revision.revision_id,
                                  'language_id': latest_revision.language_id})
        return latest_revision

    @property
    def editor(self):
        return User.from_pk(self.editor_id)

    @cached_property
    def language(self):
        return WikiLanguage.from_pk(self.language_id)


class WikiAliases(db.Model, MultiPKMixin):
    __tablename__ = 'wiki_aliases'
    __cache_key_of_article__ = 'wiki_aliases_articles_{article_id}'

    article_id: int = db.Column(db.Integer, db.ForeignKey('wiki_articles.id'), primary_key=True)
    alias: str = db.Column(db.String(128), primary_key=True)

    @classmethod
    def from_article(cls, article_id: int) -> List[str]:
        return cls.get_col_from_many(
            key=cls.__cache_key_of_article__.format(article_id=article_id),
            column=cls.alias,
            filter=cls.article_id == article_id,
            order=cls.alias.asc())

    @classmethod
    def new(cls, article_id: int, alias: str) -> Optional['WikiAliases']:
        if cls.from_attrs(alias=alias):
            raise WikiAliasAlreadyExists
        return cls._new(article_id=article_id, alias=alias)


class WikiLanguage(db.Model, SinglePKMixin):
    __tablename__ = 'wiki_languages'
    __cache_key__ = 'wiki_language_{id}'
    __cache_key_from_language = 'wiki_language_lang_{language}'

    id: int = db.Column(db.Integer, primary_key=True)
    language: str = db.Column(db.String(128), nullable=False, unique=True)

    @classmethod
    def from_language(cls, language: str, error: bool = False) -> Optional['WikiLanguage']:
        language = language.lower()
        wiki_language = cls.from_query(
            key=cls.__cache_key_from_language.format(language=language),
            filter=func.lower(cls.language) == language)
        if error and not wiki_language:
            raise APIException(f'Invalid {WikiLanguage} {language}.')
        return wiki_language
