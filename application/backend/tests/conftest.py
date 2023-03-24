import pytest
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from pytest_postgresql import factories
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.models.user import User
from app.models.slack_organization import SlackOrganization

database_name = "pizza"
postgresql = factories.postgresql_proc(dbname=database_name)


@pytest.fixture
def postgresql_url(postgresql):
    connection = f'postgresql://{postgresql.user}:{postgresql.password}@{postgresql.host}:{postgresql.port}/{postgresql.dbname}'

    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        host=postgresql.host,
        port=postgresql.port,
        password=postgresql.password
    )

    # Create the "pizza" database
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute('CREATE DATABASE %s;' % database_name)
    cur.close()
    conn.close()

    return connection


@pytest.fixture
def environment_variables(postgresql_url, monkeypatch):
    monkeypatch.setenv('FLASK_ENV', 'test')
    monkeypatch.setenv('MQ_RPC_KEY', 'dontCare')
    monkeypatch.setenv('DATABASE_URL', postgresql_url)
    monkeypatch.setenv('SECRET_KEY', 'verySuperSecretKey')


@pytest.fixture
def app(mocker, environment_variables):
    mocker.patch('app.application.broker')
    config = {
        "base": "app.config.Base",
        "test": "app.config.Test",
        "production": "app.config.Production"
    }
    # Needs to be imported here as we need to set the environment variables in the environment_variables fixture
    # before we import it
    from app.application import create_app
    app = create_app(config)
    return app


@pytest.fixture
def db(app):
    db = SQLAlchemy(app=app)
    return db


@pytest.fixture(autouse=True)
def migrate(app, db):
    migrate = Migrate(app, db)
    upgrade('../migrations')
    return migrate


@pytest.fixture
def slack_organization(app, db, migrate):
    slack_organization = SlackOrganization(team_id="testSlackOrganizationId")
    db.session.add(slack_organization)
    db.session.commit()
    return slack_organization


@pytest.fixture
def user(db, slack_organization):
    user = User(
        id="testUserId",
        email="dont@care.invalid",
        name="dontCare",
        picture="doesntExist",
        slack_organization_id=slack_organization.team_id
    )
    db.session.add(user)
    db.session.commit()
    return user
