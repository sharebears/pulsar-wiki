from core import db
from core.mixins import TestDataPopulator
from wiki.permissions import WikiPermissions


class WikiPopulator(TestDataPopulator):

    @classmethod
    def populate(cls):
        db.session.execute(
            """
            INSERT INTO wiki_articles (title, contents, last_editor_id, deleted) VALUES
            ('Wiki1', 'Contents1', 1, 'f'),
            ('Wiki2', 'Contents2', 4, 'f'),
            ('Wiki3', 'Contents3', 2, 'f'),
            ('Wiki4', 'Contents4', 1, 't')
            """)
        cls.add_permissions(
            WikiPermissions.VIEW,
            WikiPermissions.EDIT,
            WikiPermissions.CREATE,
            WikiPermissions.DELETE)
        db.session.commit()

    @classmethod
    def unpopulate(cls):
        db.engine.execute('DELETE FROM wiki_aliases')
        db.engine.execute('DELETE FROM wiki_revisions')
        db.engine.execute('DELETE FROM wiki_articles')
        db.engine.execute('ALTER SEQUENCE wiki_aliases_id_seq RESTART WITH 1')
