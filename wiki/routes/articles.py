import flask
from voluptuous import All, Any, Length, Schema, Range

from core import APIException
from core.utils import require_permission, validate_data
from wiki.models import WikiArticle, WikiTranslation, WikiRevision, WikiLanguage
from wiki.permissions import WikiPermissions

from . import bp

app = flask.current_app

VIEW_ARTICLE_SCHEMA = Schema({
    'language': All(str, Length(max=128)),
    })


@bp.route('/wiki/articles/<int:id>', methods=['GET'])
@require_permission(WikiPermissions.VIEW)
@validate_data(VIEW_ARTICLE_SCHEMA)
def view_wiki_article(id: int, language: str):
    if language:
        return flask.jsonify(WikiTranslation.from_attrs(
            article_id=id,
            language_id=WikiLanguage.from_language(language).id))
    return flask.jsonify(WikiArticle.from_pk(
        pk=id,
        _404=True,
        include_dead=flask.g.user.has_permission(WikiPermissions.VIEW_DELETED)))


CREATE_ARTICLE_SCHEMA = Schema({
    'language': All(str, Length(max=128)),
    'article_id': Any(int, None),
    'title': All(str, Range(min=1, max=128)),
    'contents': All(str, Length(max=1000000000))
    })


@bp.route('/wiki/create', methods=['POST'])
@require_permission(WikiPermissions.CREATE)
@validate_data(CREATE_ARTICLE_SCHEMA)
def create_wiki_article(title: str,
                        contents: str,
                        language: str = None,
                        article_id: int = None):
    if language and WikiArticle.is_valid(article_id):
        language_id = WikiLanguage.from_language(language, error=True)
        wiki = WikiTranslation.new(
            article_id=article_id,
            title=title,
            language_id=language_id,
            contents=contents,
            user_id=flask.g.user.id)
    else:
        wiki = WikiArticle.new(
            title=title,
            contents=contents,
            user_id=flask.g.user.id)
    return flask.jsonify(wiki)


EDIT_ARTICLE_SCHEMA = Schema({
    'title': All(str, Range(mix=1, max=128)),
    'language': All(str, Length(max=128)),
    'contents': All(str, Length(max=1000000000))
    })


@bp.route('/wiki/modify/<int:id>', methods=['PUT'])
@require_permission(WikiPermissions.EDIT)
@validate_data(EDIT_ARTICLE_SCHEMA)
def edit_wiki_article(id: int,
                      title: str,
                      language: str,
                      contents: str):
    wiki = WikiArticle.from_pk(id, _404=True)
    if not wiki:
        raise APIException(f'WikiArticle {id} does not exist.')
    language_id = WikiLanguage.from_language(language, error=True)
    wiki = WikiRevision.new(article_id=id,
                            title=title,
                            language_id=language_id,
                            editor_id=flask.g.user.id,
                            contents=contents)
    return wiki
