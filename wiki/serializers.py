from core.mixins import Attribute, Serializer


class WikiArticleSerializer(Serializer):
    id = Attribute()
    title = Attribute()
    contents = Attribute()
    revision = Attribute()
    last_updated = Attribute()
    last_editor_id = Attribute(nested=('id', 'username', ))


class WikiArticleRevision(Serializer):
    id = Attribute()
    wiki_id = Attribute()
    title = Attribute()
    editor_id = Attribute(nested=('id', 'username', ))
    time_created = Attribute()
    contents = Attribute()
    revision = Attribute()
