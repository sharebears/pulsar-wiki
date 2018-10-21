from core.mixins import Attribute, Serializer


class WikiArticleSerializer(Serializer):
    id = Attribute()
    title = Attribute()
    contents = Attribute()
    aliases = Attribute()
    latest_revision = Attribute()
    languages = Attribute()


class WikiRevisionSerializer(Serializer):
    revision_id = Attribute()
    language = Attribute()
    parent_article = Attribute(nested=False)
    title = Attribute()
    editor = Attribute(nested=('id', 'username', ))
    time = Attribute()
    contents = Attribute()


class WikiTranslationSerializer(Serializer):
    parent_article = Attribute()
    language = Attribute()
    title = Attribute()
    contents = Attribute()
    latest_revision = Attribute()


class WikiLanguageSerializer(Serializer):
    id = Attribute()
    language = Attribute()
