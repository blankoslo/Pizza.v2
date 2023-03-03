import requests
import base64
import logging
import os
import time
from functools import wraps
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.state_store import FileOAuthStateStore

from src.api.bot_api import BotApi, BotApiConfiguration
from src.injector import injector
from src.slack.installation_store import BrokerInstallationStore
from src.api.slack_api import SlackApi

pizza_channel_id = os.environ["PIZZA_CHANNEL_ID"]
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
client_id = os.environ["SLACK_CLIENT_ID"],
client_secret = os.environ["SLACK_CLIENT_SECRET"],
slack_app_token = os.environ["SLACK_APP_TOKEN"]

slack_app = App(
    signing_secret=slack_signing_secret,
    installation_store=BrokerInstallationStore(),
    oauth_settings=OAuthSettings(
        client_id=client_id,
        client_secret=client_secret,
        state_store=FileOAuthStateStore(expiration_seconds=600),
        #scopes=os.environ["SLACK_SCOPES"].split(","),
    ),
)
slack_handler = SocketModeHandler(slack_app, slack_app_token)

def request_time_monitor(timeout=3000):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = injector.get(logging.Logger)
            start_time = time.time()
            user_id = None
            if "body" in kwargs and "event" in kwargs["body"]:
                user_id = kwargs["body"]["event"].get("user")
                if user_id is None:
                    user_id = kwargs["body"]["event"].get("user_id")
            elif "body" in kwargs and "user" in kwargs["body"]:
                user_id = kwargs["body"]["user"].get("id")
            response = func(*args, **kwargs)
            end_time = time.time()
            execution_time = round((end_time - start_time) * 1000, 2)
            # Log execution time of function if over timeout limit as using more than the timeout limit usually
            # means that the slack request will fail and the user will get a ⚠️
            if execution_time > timeout:
                logger.warn(f"Function {func.__name__} took {execution_time}ms to execute. User ID: {user_id}")
            return response
        return wrapper
    return decorator

@slack_app.event("message")
@request_time_monitor()
def handle_event(body, say, context):
    event = body["event"]
    token = context["token"]
    client = SlackApi(client=context["client"])
    # Handle a file share
    if "subtype" in event and event["subtype"] == 'file_share':
        handle_file_share(event=event, say=say, token=token, client=client)

def handle_rsvp(body, ack, attending, client):
    user = body["user"]
    user_id = user["id"]
    channel = body["channel"]
    channel_id = channel["id"]
    message = body["message"]
    with injector.get(BotApi) as ba:
        invited_users = ba.get_invited_users()
        if user_id in invited_users:
            ts = message['ts']
            event_id = body["actions"][0]["value"]
            blocks = message["blocks"][0:3]
            if attending:
                ba.accept_invitation(event_id=event_id, slack_id=user_id)
            else:
                ba.decline_invitation(event_id=event_id, slack_id=user_id)
                ba.invite_multiple_if_needed()
            ba.send_pizza_invite_answered(channel_id=channel_id, ts=ts, event_id=event_id, old_blocks=blocks, attending=attending, slack_client=client)
    ack()

@slack_app.action("rsvp_yes")
@request_time_monitor()
def handle_rsvp_yes(ack, body, context):
    client = SlackApi(client=context["client"])
    handle_rsvp(body=body, ack=ack, attending=True, client=client)

@slack_app.action("rsvp_no")
@request_time_monitor()
def handle_rsvp_no(ack, body, context):
    client = SlackApi(client=context["client"])
    handle_rsvp(body=body, ack=ack, attending=False, client=client)

@slack_app.action("rsvp_withdraw")
@request_time_monitor()
def handle_rsvp_withdraw(ack, body, context):
    logger = injector.get(logging.Logger)
    client = SlackApi(client=context["client"])
    message = body["message"]
    user = body["user"]
    user_id = user["id"]
    channel = body["channel"]
    channel_id = channel["id"]
    event_id = body["actions"][0]["value"]
    ts = message['ts']
    blocks = message["blocks"][0:3]
    with injector.get(BotApi) as ba:
        success = ba.withdraw_invitation(event_id=event_id, slack_id=user_id)
        if success:
            logger.info("%s withdrew their invitation", user_id)
            ba.send_pizza_invite_withdraw(channel_id=channel_id, ts=ts, old_blocks=blocks, slack_client=client)
        else:
            logger.warning("failed to withdraw invitation for %s", user_id)
            ba.send_pizza_invite_withdraw_failure(channel_id=channel_id, ts=ts, old_blocks=blocks, slack_client=client)
    ack()

def handle_file_share(event, say, token, client):
    channel = event["channel"]
    if 'files' in event:
        files = event['files']
        with injector.get(BotApi) as ba:
            ba.send_slack_message_old(channel_id=channel, text=u'Takk for fil! 🤙', slack_client=client)
            headers = {u'Authorization': u'Bearer %s' % token}
            for file in files:
                r = requests.get(
                    file['url_private'], headers=headers)
                b64 = base64.b64encode(r.content).decode('utf-8')
                payload = {'file': 'data:image;base64,%s' % b64,
                           'upload_preset': 'blank.pizza'}
                r2 = requests.post(
                    'https://api.cloudinary.com/v1_1/blank/image/upload', data=payload)
                ba.save_image(
                    r2.json()['public_id'], file['user'], file['title'])

# We don't use app mentions at the moment, but perhaps it'll be useful in the future
@slack_app.event("app_mention")
@request_time_monitor()
def handle_mention_event(body):
    pass

# This only exists to make bolt not throw a warning that we dont handle the file_shared event
# We dont use this as we use the message event with subtype file_shared as that one
# contains a full file object with url_private, while this one only contains the ID
# Perhaps another file event contains the full object?
@slack_app.event("file_shared")
@request_time_monitor()
def handle_file_shared_events(body):
    pass
