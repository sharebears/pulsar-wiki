from core.mixins import Attribute, Serializer


class WikiArticleSerializer(Serializer):
    id = Attribute()
    title = Attribute()
    contents = Attribute()
    aliases = Attribute()
    last_updated = Attribute()
    latest_revision_id = Attribute()


class WikiArticleRevisionSerializer(Serializer):
    revision_id = Attribute()
    article_id = Attribute()
    title = Attribute()
    editor = Attribute(nested=('id', 'username', ))
    time_created = Attribute()
    contents = Attribute()
    language = Attribute()


class WikiTranslationSerializer(Serializer):
    parent_article = Attribute()
    language = Attribute()
    title = Attribute()
    contents = Attribute()
    last_updated = Attribute()
    latest_revision_id = Attribute()
