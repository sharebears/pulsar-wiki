import flask
from coluptous import All, Length, Schema

from core.utils import require_permission, validate_data
from wiki.models import Wiki

from . import bp

app = flask.current_app

VIEW_WIKI_SCHEMA = Schema({
    'language': All(str, Length(max-32))
    })


@bp.route('/wiki/<int:id>', methods=['GET'])
@require_permission('wiki_view')
@validate_data(VIEW_WIKI_SCHEMA)
def view_wiki(id: int, language: str) -> flask.Response:
    return flask.jsonify(Wiki.from_pk(
                                    id,
                                    _404=True,
                                    include_dead=flask.g.user.has_permission('wiki_modify_advanced')))
