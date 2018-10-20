from core.mixins import Attribute, Serializer


class WikiArticleSerializer(Serializer):
    id = Attribute()
    title = Attribute()
    contents = Attribute()
    aliases = Attribute()
    latest_revision_id = Attribute()


class WikiArticleRevisionSerializer(Serializer):
    article_id = Attribute()
    revision_id = Attribute()
    title = Attribute()
    editor = Attribute(nested=('id', 'username', ))
    time = Attribute()
    contents = Attribute()
    language = Attribute()


class WikiTranslationSerializer(Serializer):
    parent_article = Attribute()
    language = Attribute()
    title = Attribute()
    contents = Attribute()
    latest_revision_id = Attribute()
