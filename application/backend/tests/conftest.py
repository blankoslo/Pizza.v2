import pytest
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from pytest_postgresql import factories

postgresql = factories.postgresql_proc()

@pytest.fixture(scope='session')
def postgresql_url(postgresql):
    return f'postgresql://{postgresql.user}:{postgresql.password}@{postgresql.host}:{postgresql.port}/{postgresql.dbname}'

@pytest.fixture
def environment_variables(postgresql_url, monkeypatch):
    monkeypatch.setenv('FLASK_ENV', 'test')
    monkeypatch.setenv('MQ_RPC_KEY', 'dontCare')
    monkeypatch.setenv('DATABASE_URL', postgresql_url)

@pytest.fixture
def app(mocker, environment_variables):
    mocker.patch('app.broker')
    config = {
        "base": "app.config.Base",
        "test": "app.config.Test",
        "production": "app.config.Production"
    }
    # Needs to be imported here as we need to set the environment variables in the environment_variables fixture
    # before we import it
    from app import create_app
    app = create_app(config)
    return app

@pytest.fixture
def db(app):
    db = SQLAlchemy(app=app)
    db.create_all()
    yield db
    db.drop_all()

@pytest.fixture(scope='session')
def migrate(app, db):
    migrate = Migrate(app, db)
    return migrate
