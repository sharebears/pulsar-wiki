from datetime import datetime
from typing import List

import flask
from sqlalchemy import func

from core import cache, db
from core.mixins import SinglePKMixin
from core.users.models import User
from core.utils import cached_property
from wiki.serializers import WikiArticleRevisionSerializer, WikiArticleSerializer

app = flask.current_app


class WikiArticle(db.Model, SinglePKMixin):
    __tablename__ = 'wiki_articles'
    __serializer__ = WikiArticleSerializer
    __cache_key__ = 'wiki_articles_{id}'
    __cache_key_all__ = 'wiki_articles_all'

    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String(128), nullable=False)
    contents: str = db.Column(db.Text, nullable=False)
    last_editor_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    last_updated: datetime = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now())
    revision: int = db.Column(db.Integer, nullable=False)
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


class WikiArticleRevision(db.Model, SinglePKMixin):
    __tablename__ = 'wiki_articles_revisions'
    __serializer__ = WikiArticleRevisionSerializer
    __cache_key__ = 'wiki_revisions_{id}'
    __cache_key_of_article__ = 'wiki_revisions_article_{article_id}'

    id: int = db.Column(db.Integer, primary_key=True)
    article_id: int = db.Column(db.Integer, db.ForeignKey('wiki_articles.id'), nullable=False)
    title: str = db.Column(db.String(128), nullable=False)
    editor_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    time_created: datetime = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now())
    contents: str = db.Column(db.Text, nullable=False)
    revision: int = db.Column(db.Integer, nullable=False)

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


class WikiArticleAliases(db.Model, SinglePKMixin):
    __tablename__ = 'wiki_articles_aliases'
    __cache_key__ = 'wiki_articles_alias_{id}'

    id: int = db.Column(db.Integer, primary_key=True)
    article_id: int = db.Column(db.Integer, db.ForeignKey('wiki_articles.id'), nullable=False)
    alias: str = db.Column(db.String(128), nullable=False)
