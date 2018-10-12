from werkzeug import find_modules, import_string

from wiki import routes

# Start all permission names with 'wiki_'.

PERMISSIONS = [
    'wiki_view',  # View the wiki
    ]


def init_app(app):
    with app.app_context():
        for name in find_modules('wiki', recursive=True):
            import_string(name)
        app.register_blueprint(routes.bp)
