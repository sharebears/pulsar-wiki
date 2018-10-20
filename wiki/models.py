from datetime import datetime
from typing import List, Optional

import flask
from sqlalchemy import func

from core import cache, db
from core.mixins import SinglePKMixin, MultiPKMixin
from core.users.models import User
from core.utils import cached_property
from wiki.serializers import WikiArticleRevisionSerializer, WikiArticleSerializer

app = flask.current_app


class WikiArticle(db.Model, SinglePKMixin):
    __tablename__ = 'wiki_articles'
    __cache_key__ = 'wiki_articles_{id}'
    __cache_key_all__ = 'wiki_articles_all'
    __serializer__ = WikiArticleSerializer

    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String(128), nullable=False)
    contents: str = db.Column(db.Text, nullable=False)
    last_editor_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    last_updated: datetime = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now())
    deleted: bool = db.Column(db.Boolean, nullable=False, server_default='f', index=True)

    @classmethod
    def get_all(cls, include_dead: bool = False) -> List['WikiArticle']:
        return cls.get_many(
            key=cls.__cache_key_all,
            include_dead=include_dead,
            required_properties=('last_editor', ))

    @classmethod
    def new(cls,
            title: str,
            contents: str,
            revision: int,
            last_editor_id: int) -> 'WikiArticle':
        User.is_valid(last_editor_id, error=True)
        cache.delete(cls.__cache_key_all__.format)
        return super()._new(
            title=title,
            contents=contents,
            revision=revision,
            last_editor_id=last_editor_id)

    @cached_property
    def last_editor(self):
        return User.from_pk(self.last_editor_id)

    @cached_property
    def aliases(self):
        return WikiArticleAliases.from_article(self.id)

    @cached_property
    def latest_revision_id(self):
        return WikiArticleRevision.latest_id_from_article(self.id)


class WikiArticleRevision(db.Model, MultiPKMixin):
    __tablename__ = 'wiki_articles_revisions'
    __cache_key__ = 'wiki_articles_revisions_{article_id}_{revision_id}'
    __cache_key_of_article__ = 'wiki_articles_revisions_of_article_{article_id}'
    __cache_key_latest_id_of_article__ = 'wiki_articles_revisions_latest_{article_id}'
    __serializer__ = WikiArticleRevisionSerializer

    revision_id: int = db.Column(db.Integer, primary_key=True)
    article_id: int = db.Column(db.Integer, db.ForeignKey('wiki_articles.id'), primary_key=True)
    title: str = db.Column(db.String(128), nullable=False)
    editor_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    time_created: datetime = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now())
    contents: str = db.Column(db.Text, nullable=False)

    @classmethod
    def from_article(cls,
                     article_id: int,
                     page: int = 1,
                     limit: int = 50) -> List['WikiArticleRevision']:
        return cls.get_many(
            key=cls.__cache_key_of_article__.format(article_id=article_id),
            filter=cls.article_id == article_id,
            order=cls.time_created.desc(),
            page=page,
            limit=limit)

    @classmethod
    def new(cls,
            article_id: int,
            title: str,
            editor_id: int,
            contents: str) -> Optional['WikiArticleRevision']:
        WikiArticle.is_valid(article_id, error=True)
        old_latest_id = cls.latest_id_from_article(article_id) + 1
        cache.inc(cls.__cache_key_latest_id_of_article__.format(article_id=article_id))
        return super()._new(
            revision_id=old_latest_id,
            article_id=article_id,
            title=title,
            editor_id=editor_id,
            contents=contents)

    @classmethod
    def latest_id_from_article(cls, article_id: int) -> int:
        cache_key = cls.__cache_key_latest_id_of_article__.format(article_id=article_id)
        latest_id = cache.get(cache_key)
        if not latest_id:
            latest_id = (db.session.query(cls.revision_id)
                         .filter(cls.article_id == article_id)
                         .order_by(cls.revision_id.desc())
                         .limit(1))
            latest_id = latest_id[0] if latest_id else 0
            cache.set(cache_key, latest_id)
        return latest_id

    @property
    def editor(self):
        return User.from_pk(self.editor_id)


class WikiArticleAliases(db.Model, MultiPKMixin):
    __tablename__ = 'wiki_articles_aliases'
    __cache_key_of_article__ = 'wiki_articles_aliases_article_{article_id}'

    article_id: int = db.Column(db.Integer, db.ForeignKey('wiki_articles.id'), primary_key=True)
    alias: str = db.Column(db.String(128), primary_key=True)

    @classmethod
    def from_article(cls, article_id: int) -> List[str]:
        return cls.get_col_from_many(
            key=cls.__cache_key_of_article__.format(article_id=article_id),
            column=cls.alias,
            filter=cls.article_id == article_id,
            order=cls.alias.asc())
