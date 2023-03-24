import pytest
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from pytest_postgresql import factories
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.models.user import User
from app.models.slack_organization import SlackOrganization
from app.models.restaurant import Restaurant
from app.models.event import Event
from sqlalchemy import text

database_name = "pizza"
postgresql = factories.postgresql_proc(dbname=database_name)

@pytest.fixture(scope='session')
def postgresql_database(postgresql):
    conn = psycopg2.connect(
        dbname='postgres',
        user=postgresql.user,
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

    yield postgresql


@pytest.fixture
def postgresql_url(postgresql_database):
    return f'postgresql://{postgresql_database.user}:{postgresql_database.password}@{postgresql_database.host}:{postgresql_database.port}/{postgresql_database.dbname}'


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
    db.session.execute(text('DROP SCHEMA public CASCADE'))
    # create the public schema
    db.session.execute(text('CREATE SCHEMA public'))
    # commit the changes
    db.session.commit()
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


@pytest.fixture
def restaurant(db, slack_organization):
    restaurant = Restaurant(
        name="dontCare",
        slack_organization_id=slack_organization.team_id
    )
    db.session.add(restaurant)
    db.session.commit()
    return restaurant

@pytest.fixture
def events(db, restaurant, slack_organization):
    event1 = Event(
        time="2023-03-30T16:23:05.420Z",
        restaurant_id=restaurant.id,
        people_per_event=5,
        slack_organization_id=slack_organization.team_id
    )
    event2 = Event(
        time="2023-04-24T16:23:05.420Z",
        restaurant_id=restaurant.id,
        people_per_event=5,
        slack_organization_id=slack_organization.team_id
    )
    db.session.add(event1)
    db.session.add(event2)
    db.session.commit()
    return [event1, event2]
