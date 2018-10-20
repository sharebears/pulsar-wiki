import flask
from voluptuous import All, Length, Schema

from core.utils import require_permission, validate_data
from wiki.models import WikiArticle, WikiTranslation, WikiLanguage
from wiki.permissions import WikiPermissions

from . import bp

app = flask.current_app

VIEW_ARTICLE_SCHEMA = Schema({
    'language': All(str, Length(max=128)),
    })


@bp.route('/wiki/articles/<int:id>', methods=['GET'])
@require_permission(WikiPermissions.VIEW)
@validate_data(VIEW_ARTICLE_SCHEMA)
def view_wiki(id: int, language: str):
    if language:
        return flask.jsonify(WikiTranslation.from_attrs(
            article_id=id,
            language_id=WikiLanguage.from_language(language).id))
    return flask.jsonify(WikiArticle.from_pk(
        pk=id,
        _404=True,
        include_dead=flask.g.user.has_permission(WikiPermissions.VIEW_DELETED)))
