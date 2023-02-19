from marshmallow import fields, Schema
from src.broker.schemas.slack_message import SlackMessage

class GetUnansweredInvitationsDataSchema(Schema):
    slack_id = fields.Str(required=True)
    event_id = fields.UUID(required=True)
    invited_at = fields.DateTime(required=True)
    reminded_at = fields.DateTime(required=True)
    slack_message = fields.Nested(SlackMessage)

class GetUnansweredInvitationsResponseSchema(Schema):
    invitations = fields.Nested(GetUnansweredInvitationsDataSchema, many=True)
