from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bootstrap = Bootstrap()

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)

    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')

    from app.user import bp as user_bp
    app.register_blueprint(user_bp)

    from app.error import bp as error_bp
    app.register_blueprint(error_bp)

    return app
