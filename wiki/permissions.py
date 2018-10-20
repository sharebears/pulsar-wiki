from core.permissions import PermissionsEnum


class WikiPermissions(PermissionsEnum):
    VIEW = 'wiki_view'
    VIEW_DELETED = 'wiki_view_deleted'
    EDIT = 'wiki_edit_article'
    CREATE = 'wiki_create_article'
    DELETE = 'wiki_delete_article'
