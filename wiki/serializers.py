from core.mixins import Attribute, Serializer

class WikiSerializer(Serializer):
    id = Attribute()
    title = Attribute()
    contents:= Attribute()
    version = Attribute()
    last_updated = Attribute()
    last_edited_by = Attribute(nested=('id', 'username', ))
    deleted = Attribute(permission='modify_wiki')
