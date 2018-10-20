from core.mixins import Attribute, Serializer


class WikiArticleSerializer(Serializer):
    id = Attribute()
    title = Attribute()
    contents = Attribute()
    aliases = Attribute()
    last_editor = Attribute(nested=('id', 'username', ))
    last_updated = Attribute()
    latest_revision_id = Attribute()


class WikiArticleRevisionSerializer(Serializer):
    revision_id = Attribute()
    article_id = Attribute()
    title = Attribute()
    editor = Attribute(nested=('id', 'username', ))
    time_created = Attribute()
    contents = Attribute()
