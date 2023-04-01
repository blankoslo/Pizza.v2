from app.db import db
from app.models.mixins import get_field
from app.models.image import Image
from app.models.slack_user_schema import SlackUserSchema, SlackUserResponseSchema

from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

class ImageSchema(SQLAlchemySchema):
    class Meta:
        model = Image
        include_relationships = True
        sqla_session = db.session
        load_instance = True

    cloudinary_id = auto_field()
    uploaded_by_id = auto_field()
    uploaded_by = fields.Nested(SlackUserSchema, dump_only=True)
    uploaded_at = auto_field()
    title = auto_field()

class ImageResponseSchema(ImageSchema):
    uploaded_by = fields.Nested(SlackUserResponseSchema, dump_only=True)

class ImageQueryArgsSchema(Schema):
    order = fields.Str()
    uploaded_by_id = get_field(ImageSchema, Image.uploaded_by_id)
