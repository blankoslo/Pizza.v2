import uuid
import json
import os
import logging
import time

from marshmallow import Schema

from src.injector import injector, inject
from src.broker.amqp_connection import AmqpConnection
from src.broker.schemas.message import MessageSchema
from src.broker.schemas.invite_multiple_if_needed import InviteMultipleIfNeededResponseSchema
from src.broker.schemas.get_unanswered_invitations import GetUnansweredInvitationsResponseSchema
from src.broker.schemas.update_invitation import UpdateInvitationRequestSchema, UpdateInvitationResponseSchema
from src.broker.schemas.get_invited_unanswered_user_ids import GetInvitedUnansweredUserIdsResponseSchema
from src.broker.schemas.update_slack_user import UpdateSlackUserRequestSchema, UpdateSlackUserResponseSchema
from src.broker.schemas.create_image import CreateImageRequestSchema, CreateImageResponseSchema
from src.broker.schemas.withdraw_invitation import WithdrawInvitationRequestSchema, WithdrawInvitationResponseSchema
from src.broker.schemas.get_slack_installation import GetSlackInstallationRequestSchema, GetSlackInstallationResponseSchema
from src.broker.schemas.get_slack_organizations import GetSlackOrganizationsResponseSchema
from src.broker.schemas.deleted_slack_organization_event import DeletedSlackOrganizationEventSchema
from src.broker.schemas.set_slack_channel import SetSlackChannelRequestSchema, SetSlackChannelResponseSchema

class BrokerClient:
    messages = {}

    @inject
    def __init__(self, amqp_connection: AmqpConnection, logger: logging.Logger):
        self.logger = logger
        self.mq = amqp_connection
        self.rpc_key = os.environ["MQ_RPC_KEY"]
        self.timeout = 30
        self.mq.connect()
        self.mq.setup_exchange()

        result = self.mq.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        self.mq.channel.queue_bind(self.callback_queue, exchange=self.mq.exchange)

    def disconnect(self):
        self.mq.disconnect()

    def on_response(self, ch, method, props, body):
        self.messages[props.correlation_id] = (body, method.delivery_tag)

    def _call(self, type, payload=None, ingoing_schema=None, outgoing_schema=None):
        if payload is not None and outgoing_schema is not None:
            payload = outgoing_schema().load(payload)
        message = self._create_request(type, payload)

        response = None
        corr_id = str(uuid.uuid4())

        self.mq.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response
        )

        self.mq.publish_rpc(self.rpc_key, self.callback_queue, corr_id, json.dumps(message, default=str))

        start = time.time()
        while corr_id not in self.messages:
            if time.time() - start >= self.timeout:
                break

            self.mq.connection.process_data_events(time_limit=0.1)

        if corr_id in self.messages:
            message_response = self.messages.pop(corr_id)
            try:
                response = json.loads(message_response[0].decode('utf8'))
                if ingoing_schema is not None:
                    response = ingoing_schema().load(response)
                self.mq.channel.basic_ack(delivery_tag=message_response[1])
            except Exception as e:
                response = None
                self.logger.error("Failed to handle message with error %s", repr(e))
                self.mq.channel.basic_reject(delivery_tag=message_response[1], requeue=False)
        else:
            self.logger.error("Failed to get response from backend")
        return response

    def _create_request(self, type: str, payload: Schema = None):
        request_data = {
            "type": type
        }
        if payload is not None:
            request_data['payload'] = payload
        request_schema = MessageSchema()
        request = request_schema.load(request_data)
        return request

    def deleted_slack_organization_event(self, team_id, enterprise_id=None):
        request_payload = {
            "team_id": team_id
        }
        if enterprise_id is not None:
            request_payload['enterprise_id'] = enterprise_id

        self._call(
            type="deleted_slack_organization_event",
            payload=request_payload,
            outgoing_schema=DeletedSlackOrganizationEventSchema
        )

    def set_slack_channel(self, channel_id, team_id):
        request_payload = {
            "channel_id": channel_id,
            "team_id": team_id
        }
        response = self._call(
            type="set_slack_channel",
            payload=request_payload,
            outgoing_schema=SetSlackChannelRequestSchema,
            ingoing_schema=SetSlackChannelResponseSchema
        )
        if response is None:
            return False
        return response

    def get_slack_installation(self, team_id: str):
        request_payload = {
            "team_id": team_id,
        }
        return self._call(
            type="get_slack_installation",
            payload=request_payload,
            outgoing_schema=GetSlackInstallationRequestSchema,
            ingoing_schema=GetSlackInstallationResponseSchema
        )

    def get_slack_organizations(self):
        response = self._call(type="get_slack_organizations", ingoing_schema=GetSlackOrganizationsResponseSchema)
        if response is None:
            return []
        return response['organizations']

    def invite_multiple_if_needed(self):
        response = self._call(type="invite_multiple_if_needed", ingoing_schema=InviteMultipleIfNeededResponseSchema)
        if response is None:
            return []
        return response['events']

    def get_unanswered_invitations(self):
        response = self._call(type="get_unanswered_invitations", ingoing_schema=GetUnansweredInvitationsResponseSchema)
        if response is None:
            return []
        return response['invitations']

    def get_unanswered_invitations_on_finished_events_and_set_not_attending(self):
        response = self._call(
            type="get_unanswered_invitations_on_finished_events_and_set_not_attending",
            ingoing_schema=GetUnansweredInvitationsResponseSchema
        )
        if response is None:
            return []
        return response['invitations']

    def update_invitation(self, slack_id: str, event_id: str, update_values: dict):
        request_payload = {
            "slack_id": slack_id,
            "event_id": event_id,
            "update_data": update_values
        }
        response = self._call(
            "update_invitation",
            payload=request_payload,
            outgoing_schema=UpdateInvitationRequestSchema,
            ingoing_schema=UpdateInvitationResponseSchema
        )
        if response is None:
            return False
        return response['success']

    def get_invited_unanswered_user_ids(self):
        response = self._call(
            type="get_invited_unanswered_user_ids",
            ingoing_schema=GetInvitedUnansweredUserIdsResponseSchema
        )
        if response is None:
            return []
        return response['user_ids']

    def update_slack_user(self, slack_users):
        request_payload = {
            'users_to_update': []
        }
        for slack_user in slack_users:
            slack_id = slack_user['id']
            current_username = slack_user['name']
            email = slack_user['profile']['email']
            team_id = slack_user['team_id']


            request_payload['users_to_update'].append({
                'slack_id': slack_id,
                'current_username': current_username,
                'email': email,
                'team_id': team_id
            })
        response = self._call(
            type="update_slack_user",
            payload=request_payload,
            outgoing_schema=UpdateSlackUserRequestSchema,
            ingoing_schema=UpdateSlackUserResponseSchema
        )
        if response is None:
            return UpdateSlackUserResponseSchema().load({
                'success': False,
                'updated_users': [],
                'failed_users': [user['slack_id'] for user in request_payload['users_to_update']]
            })
        return response

    def create_image(self, cloudinary_id, slack_id, team_id, title):
        request_payload = {
            "cloudinary_id": cloudinary_id,
            "slack_id": slack_id,
            'title': title,
            'team_id': team_id
        }
        response = self._call(
            type="create_image",
            payload=request_payload,
            outgoing_schema=CreateImageRequestSchema,
            ingoing_schema=CreateImageResponseSchema
        )
        if response is None:
            return False
        return response['success']

    def withdraw_invitation(self, event_id, slack_id):
        request_payload = {
            "slack_id": slack_id,
            'event_id': event_id
        }
        response = self._call(
            type="withdraw_invitation",
            payload=request_payload,
            outgoing_schema=WithdrawInvitationRequestSchema,
            ingoing_schema=WithdrawInvitationResponseSchema
        )
        if response is None:
            return False
        return response['success']
