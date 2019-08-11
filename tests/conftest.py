import pytest
from flask_migrate import upgrade

from config import TestConfig
from app import create_app, db, migrate


@pytest.fixture
def client():
    app = create_app(TestConfig)
    db.init_app(app)
    migrate.init_app(app, db)
    with app.test_client() as client:
        with app.app_context():
            upgrade()
        yield client
