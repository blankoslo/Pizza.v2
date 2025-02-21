from marshmallow import fields, Schema
from src.broker.schemas.slack_message import SlackMessage

class DeletedEventEventDataSchema(Schema):
    user_id = fields.Str(required=True)
    invitation_message = fields.Nested(SlackMessage)

class DeletedEventEventSchema(Schema):
    is_finalized = fields.Boolean(required=True)
    event_id = fields.UUID(required=True)
    timestamp = fields.DateTime(required=True)
    restaurant_name = fields.Str(required=True)
    slack = fields.Nested(DeletedEventEventDataSchema, many=True)
    team_id = fields.Str(required=True)
    bot_token = fields.Str(required=True)
    channel_id = fields.Str(required=True)
