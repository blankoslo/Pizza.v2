from app.db import db
from app.models.mixins import get_field, CrudMixin
from app.models.slack_user_schema import SlackUserSchema, SlackUserResponseSchema
from app.models.group import Group

from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field


class GroupSchema(SQLAlchemySchema):
    class Meta:
        model = Group
        include_relationships = True
        sqla_session = db.session
        load_instance = True

    id = auto_field()
    name = auto_field()
    members = fields.Nested(SlackUserSchema, many=True, dump_only=True)
