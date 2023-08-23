import logging
import os
import time
from functools import wraps
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.state_store import FileOAuthStateStore

from src.injector import injector
from src.slack.installation_store import BrokerInstallationStore
from src.slack.handlers import handle_message_event, handle_rsvp_yes, handle_rsvp_no, handle_rsvp_withdraw, handle_set_channel_command, handle_file_shared_events

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
    ),
)
# Enable delete_installation handling in the Installation store
slack_app.enable_token_revocation_listeners()
# Enable socket mode
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


# Register slack handlers
# Use direct calls instead of decorators to be able to test handlers in unit tests while slack_bolt is mocked
def register_slack_handlers():
    slack_app.event("message")(request_time_monitor()(handle_message_event))
    slack_app.action("rsvp_yes")(request_time_monitor()(handle_rsvp_yes))
    slack_app.action("rsvp_no")(request_time_monitor()(handle_rsvp_no))
    slack_app.action("rsvp_withdraw")(request_time_monitor()(handle_rsvp_withdraw))
    slack_app.command("/set-pizza-channel")(request_time_monitor()(handle_set_channel_command))
    slack_app.event("file_shared")(request_time_monitor()(handle_file_shared_events))
