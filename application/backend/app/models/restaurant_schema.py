from app.db import db
from app.models.mixins import get_field
from app.models.restaurant import Restaurant
from app.models.slack_organization_schema import SlackOrganizationSchema

from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field


class RestaurantSchema(SQLAlchemySchema):
    class Meta:
        model = Restaurant
        include_relationships = True
        sqla_session = db.session
        load_instance = True

    id = auto_field(dump_only=True)
    name = auto_field()
    link = auto_field()
    tlf = auto_field()
    address = auto_field()
    deleted = auto_field(load_only=True)
    rating = fields.Float(dump_only=True)
    slack_organization_id = auto_field()
    slack_organization = fields.Nested(SlackOrganizationSchema, dump_only=True)


class RestaurantResponseSchema(RestaurantSchema):
    class Meta(RestaurantSchema.Meta):
        exclude = ("slack_organization", "slack_organization_id")


class RestaurantUpdateSchema(SQLAlchemySchema):
    class Meta(RestaurantSchema.Meta):
        load_instance = False

    name = get_field(RestaurantSchema, Restaurant.name)
    link = get_field(RestaurantSchema, Restaurant.link)
    tlf = get_field(RestaurantSchema, Restaurant.tlf)
    address = get_field(RestaurantSchema, Restaurant.address)


class RestaurantCreateSchema(RestaurantSchema):
    class Meta(RestaurantSchema.Meta):
        exclude = ("slack_organization", "slack_organization_id", "deleted", "rating", "id")

    name = get_field(RestaurantSchema, Restaurant.name)
    link = get_field(RestaurantSchema, Restaurant.link)
    tlf = get_field(RestaurantSchema, Restaurant.tlf)
    address = get_field(RestaurantSchema, Restaurant.address)


class RestaurantQueryArgsSchema(Schema):
    name = get_field(RestaurantSchema, Restaurant.name)
