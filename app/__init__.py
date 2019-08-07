from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch
from jinja2 import Markup
from markdown import Markdown
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'user.login'
bootstrap = Bootstrap()
markdown = Markdown()

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.strip_trailing_newlines = False

    app.jinja_env.filters['markdown'] = lambda t: Markup(markdown.convert(t))

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')

    from app.user import bp as user_bp
    app.register_blueprint(user_bp)

    from app.post import bp as post_bp
    app.register_blueprint(post_bp)

    from app.mail import bp as mail_bp
    app.register_blueprint(mail_bp)

    from app.search import bp as search_bp
    app.register_blueprint(search_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from app.captcha import bp as captcha_bp
    app.register_blueprint(captcha_bp)

    from app.error import bp as error_bp
    app.register_blueprint(error_bp)

    return app
