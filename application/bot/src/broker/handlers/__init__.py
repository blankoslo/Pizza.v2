import json
from marshmallow import Schema
from src.broker.schemas.message import MessageSchema
import logging
from src.injector import injector


class MessageHandler:
    handlers = {}

    @classmethod
    def handle(cls, type_: str, incoming_schema: Schema = None):
        def decorator(func):
            cls.handlers[type_] = {
                'func': func,
                'incoming_schema': incoming_schema
            }
            return func
        return decorator

    @classmethod
    def process_message(cls, message: dict):
        type_ = message['type']
        handler = cls.handlers[type_]
        if handler['incoming_schema'] is not None:
            schema = handler['incoming_schema']()
            payload = schema.load(message.get('payload'))
            handler['func'](payload)
        else:
            handler['func']()


def on_message(channel, method, properties, body):
    logger = injector.get(logging.Logger)
    try:
        msg = body.decode('utf8')
        schema = MessageSchema()
        message = schema.load(json.loads(msg))
        logger.info('processing message of type %s', message['type'])
        MessageHandler.process_message(message)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error('failed to process message with error %s', repr(e))
        channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)

# DO NOT REMOVE: Import handlers to initialize them
# ALSO DO NOT MOVE: having it at the bottom stops circular imports
import src.broker.handlers.finalization
import src.broker.handlers.user_withdrew_after_finalization
import src.broker.handlers.deleted_event
import src.broker.handlers.updated_event
import src.broker.handlers.updated_invitation
import src.broker.handlers.new_slack_organization
