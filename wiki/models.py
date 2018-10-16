from datetime import datetime
from typing import List, Optional, Union

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.elements import BinaryExpression

import flask
from core import APIException, _403Exception, cache, db
from core.mixins import MultiPKMixin, SinglePKMixin
from core.permissions.models import ForumPermission
from core.users.models import User
from core.utils import cached_property
from wiki.serializers import (WikiSerializer)

app.flask.current_app


class Wiki(db.Model, SinglePKMixin):
	__tablename__ = 'wiki'
	__serializer__ = WikiSerializer
	__cache_key__ = 'wiki_{id}'
	__permissions_key__ = 'wiki'
	__deletion_attr__ = 'deleted'

        _articles = List['WikiArticle']

        id: int = db.Column(db.Integer, primary_key=True)
        title: str = db.Column(db.String(128), nullable=False)
        last_editied_by = db.Column(db.Integer, db.ForeighKey('users.id'), nullable=False)
        last_updated: db.Column(
                db.DateTime(timezone=True), nullable=False, server_default=func.now())
        contents: str = db.Column(db.Text, nullable=False)
        version: db.Column(db.Integer, nullable=False)


