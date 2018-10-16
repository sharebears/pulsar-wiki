from core.mixins import Attribute, Serializer


class WikiArticleSerializer(Serializer):
    id = Attribute()
    title = Attribute()
    contents = Attribute()
    version = Attribute()
    last_updated = Attribute()
    last_editor = Attribute(nested=('id', 'username', ))
    deleted = Attribute(permission='modify_wiki')
