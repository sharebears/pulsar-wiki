from core import db
from core.mixins import TestDataPopulator
from wiki.permissions import WikiPermissions


class WikiPopulator(TestDataPopulator):

    @classmethod
    def populate(cls):
        db.session.execute(  # move last updated to revisions
            """
            INSERT INTO wiki_articles (title, contents, deleted) VALUES
            ('Wiki1', 'Contents1', 'f'),
            ('Wiki2', 'Contents2', 'f'),
            ('Wiki3', 'Contents3', 'f'),
            ('Wiki4', 'Contents4', 't')
            """)
        db.session.execute(
            """INSERT INTO wiki_languages (id, language) VALUES
            (1, 'english'), (2, 'espanol'), (3, 'diddles')
            """)
        db.session.execute(
            """
            INSERT INTO wiki_translations
                (article_id, language_id, title, contents, deleted) VALUES
            (1, 2, 'WikiUno', 'ContentosUno', 'f'),
            (1, 3, 'Diddles1', 'Dontentos1', 'f'),
            (2, 2, 'WikiDos', 'ContentosDos', 'f'),
            (2, 3, 'Diddles2', 'Dontentos2', 't')
            """)
        db.session.execute(
            """
            INSERT INTO wiki_revisions
                (revision_id, article_id, language_id, title, editor_id, time, contents) VALUES
            (1, 1, 1, 'Wiki1', 2, NOW() - INTERVAL '5 DAYS', 'OldContents1'),
            (2, 1, 1, 'Wiki1', 1, NOW(), 'Contents1'),
            (1, 2, 1, 'Wiki2', 4, NOW() - INTERVAL '4 DAYS', 'Contents2'),
            (1, 3, 1, 'Wiki3', 2, NOW() - INTERVAL '2 DAYS', 'Contents3'),
            (1, 4, 1, 'Wiki4', 1, NOW() - INTERVAL '12 HOURS', 'Contents4'),
            (1, 1, 2, 'WikiUno', 2, NOW() - INTERVAL '1 DAY', 'oldContentsoEspanol1'),
            (1, 1, 3, 'Diddles1', 1, NOW() - INTERVAL '1 DAY', 'OldDontentos1'),
            (1, 2, 2, 'WikiDos', 4, NOW() - INTERVAL '1 DAY', 'OldContentosEspnaol2'),
            (1, 2, 3, 'Diddles2', 1, NOW() - INTERVAL '1 DAY', 'OldDontentos2')
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
