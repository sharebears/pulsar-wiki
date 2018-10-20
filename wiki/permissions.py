from core.permissions import PermissionsEnum


class WikiPermissions(PermissionsEnum):
    VIEW = 'wiki_view'
    EDIT = 'wiki_edit_article'
    CREATE = 'wiki_create_article'
    DELETE = 'wiki_delete_article'
