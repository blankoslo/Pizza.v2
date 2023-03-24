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
from app.models.slack_user import SlackUser
from app.models.group import Group
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
def slack_organizations(app, db, migrate):
    slack_organization1 = SlackOrganization(team_id="testSlackOrganizationId1")
    slack_organization2 = SlackOrganization(team_id="testSlackOrganizationId2")
    db.session.add(slack_organization1)
    db.session.add(slack_organization2)
    db.session.commit()
    return [
        slack_organization1,
        slack_organization2
    ]


@pytest.fixture
def users(db, slack_organizations):
    user1 = User(
        id="testUserId1",
        email="dont@care1.invalid",
        name="dontCare",
        picture="doesntExist",
        slack_organization_id=slack_organizations[0].team_id
    )
    user2 = User(
        id="testUserId2",
        email="dont@care2.invalid",
        name="dontCare",
        picture="doesntExist",
        slack_organization_id=slack_organizations[1].team_id
    )
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()
    return {
        slack_organizations[0].team_id: user1,
        slack_organizations[1].team_id: user2
    }


@pytest.fixture
def restaurant(db, slack_organizations):
    restaurant1 = Restaurant(
        name="dontCareRestaurant",
        slack_organization_id=slack_organizations[0].team_id
    )
    restaurant2 = Restaurant(
        name="dontCareRestaurant",
        slack_organization_id=slack_organizations[1].team_id
    )
    db.session.add(restaurant1)
    db.session.add(restaurant2)
    db.session.commit()
    return {
        slack_organizations[0].team_id: [restaurant1],
        slack_organizations[1].team_id: [restaurant2]
    }


@pytest.fixture
def slack_user(db, slack_organizations):
    slack_user = SlackUser(
        slack_id="dontCareSlackId",
        current_username="dontCareUsername",
        first_seen="2023-03-24T16:23:05.420Z",
        active=True,
        priority=1,
        email="dontCare@email.invalid",
        slack_organization_id=slack_organizations[0].team_id
    )
    db.session.add(slack_user)
    db.session.commit()
    return {
        slack_organizations[0].team_id: [slack_user],
        slack_organizations[1].team_id: []
    }


@pytest.fixture
def groups(db, slack_organizations, slack_user):
    group1 = Group(
        name="dontCareGroup",
        members=slack_user.get(slack_organizations[0].team_id),
        slack_organization_id=slack_organizations[0].team_id
    )
    group2 = Group(
        name="dontCareGroup",
        members=slack_user.get(slack_organizations[1].team_id),
        slack_organization_id=slack_organizations[1].team_id
    )
    db.session.add(group1)
    db.session.add(group2)
    db.session.commit()
    return {
        slack_organizations[0].team_id: [group1],
        slack_organizations[1].team_id: [group2]
    }


@pytest.fixture
def events(db, restaurant, groups, slack_organizations):
    event1 = Event(
        time="2023-03-30T16:23:05.420Z",
        restaurant_id=restaurant.get(slack_organizations[0].team_id)[0].id,
        people_per_event=5,
        slack_organization_id=slack_organizations[0].team_id,
        group_id=groups.get(slack_organizations[0].team_id)[0].id
    )
    event2 = Event(
        time="2023-04-24T16:23:05.420Z",
        restaurant_id=restaurant.get(slack_organizations[0].team_id)[0].id,
        people_per_event=5,
        slack_organization_id=slack_organizations[0].team_id
    )
    event3 = Event(
        time="2023-04-24T16:23:05.420Z",
        restaurant_id=restaurant.get(slack_organizations[1].team_id)[0].id,
        people_per_event=5,
        slack_organization_id=slack_organizations[1].team_id
    )
    db.session.add(event1)
    db.session.add(event2)
    db.session.add(event3)
    db.session.commit()
    return {
        slack_organizations[0].team_id: [event1, event2],
        slack_organizations[1].team_id: [event3]
    }
