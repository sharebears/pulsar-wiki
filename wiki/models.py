from datetime import datetime
from typing import List

import flask
from sqlalchemy import func

from core import db
from core.mixins import SinglePKMixin
from core.users.models import User
from core.utils import cached_property
from wiki.serializers import WikiArticleSerializer

app = flask.current_app


class WikiArticle(db.Model, SinglePKMixin):
    __tablename__ = 'wiki_articles'
    __serializer__ = WikiArticleSerializer
    __cache_key__ = 'wiki_articles_{id}'

    _articles = List['WikiArticle']

    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String(128), nullable=False)
    last_editor_id: int = db.Column(db.Integer, db.ForeighKey('users.id'), nullable=False)
    last_updated: datetime = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now())
    contents: str = db.Column(db.Text, nullable=False)
    version: int = db.Column(db.Integer, nullable=False)

    @cached_property
    def last_editor(self):
        return User.from_pk(self.last_editor_id)
