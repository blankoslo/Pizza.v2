import requests
import base64
import logging

from src.api.bot_api import BotApi
from src.injector import injector
from src.api.slack_api import SlackApi


def handle_message_event(ack, body, context):
    event = body["event"]
    token = context["token"]
    client = SlackApi(client=context["client"])
    # Handle a file share
    if "subtype" in event and event["subtype"] == 'file_share':
        handle_file_share(event=event, token=token, client=client)


def handle_rsvp(body, ack, attending, client):
    user = body["user"]
    user_id = user["id"]
    channel = body["channel"]
    channel_id = channel["id"]
    message = body["message"]
    ts = message['ts']
    event_id = body["actions"][0]["value"]
    blocks = message["blocks"][0:3]
    # Use bot client outside `with` to not get slowed down by getting a connection
    print(BotApi)
    print(injector)
    bot_client = injector.get(BotApi)
    # Send loading message and acknowledge the slack request
    print(bot_client)
    bot_client.send_pizza_invite_loading(channel_id=channel_id, ts=ts, old_blocks=blocks, event_id=event_id, slack_client=client)
    ack()
    with bot_client as ba:
        # Handle request
        invited_users = ba.get_invited_users()
        if user_id in invited_users:
            # Update invitation
            if attending:
                ba.accept_invitation(event_id=event_id, slack_id=user_id)
            else:
                ba.decline_invitation(event_id=event_id, slack_id=user_id)
                ba.invite_multiple_if_needed()
            # Update the user's invitation message
            ba.send_pizza_invite_answered(channel_id=channel_id, ts=ts, event_id=event_id, old_blocks=blocks, attending=attending, slack_client=client)
        else:
            # Handle user that wasn't among invited users
            ba.send_pizza_invite_not_among_invited_users(channel_id=channel_id, ts=ts, old_blocks=blocks, event_id=event_id, slack_client=client)


def handle_rsvp_yes(ack, body, context):
    client = SlackApi(client=context["client"])
    handle_rsvp(body=body, ack=ack, attending=True, client=client)


def handle_rsvp_no(ack, body, context):
    client = SlackApi(client=context["client"])
    handle_rsvp(body=body, ack=ack, attending=False, client=client)


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
    bot_client = injector.get(BotApi)
    # Send loading message and acknowledge the slack request
    bot_client.send_pizza_invite_loading(channel_id=channel_id, ts=ts, old_blocks=blocks, event_id=event_id, slack_client=client)
    ack()
    with bot_client as ba:
        # Try to withdraw the user
        success = ba.withdraw_invitation(event_id=event_id, slack_id=user_id)
        if success:
            logger.info("%s withdrew their invitation", user_id)
            ba.send_pizza_invite_withdraw(channel_id=channel_id, ts=ts, old_blocks=blocks, slack_client=client)
        else:
            logger.warning("failed to withdraw invitation for %s", user_id)
            ba.send_pizza_invite_withdraw_failure(channel_id=channel_id, ts=ts, old_blocks=blocks, slack_client=client)


def handle_file_share(event, token, client):
    channel = event["channel"]
    if 'files' in event and 'thread_ts' not in event:
        files = event['files']
        with injector.get(BotApi) as ba:
            ba.send_slack_message(channel_id=channel, text=u'Takk for fil! 🤙', slack_client=client)
            headers = {u'Authorization': u'Bearer %s' % token}
            for file in files:
                r = requests.get(
                    file['url_private'], headers=headers)
                b64 = base64.b64encode(r.content).decode('utf-8')
                payload = {
                    'file': 'data:image;base64,%s' % b64,
                    'upload_preset': 'blank.pizza.v2',
                    'tags': ','.join(['pizza', file['user_team']])
                }
                r2 = requests.post(
                    'https://api.cloudinary.com/v1_1/blank/image/upload', data=payload)
                ba.save_image(
                    cloudinary_id=r2.json()['public_id'],
                    slack_id=file['user'],
                    team_id=file['user_team'],
                    title=file['title'])


def handle_set_channel_command(ack, body, context):
    ack()
    with injector.get(BotApi) as ba:
        team_id = body["team_id"]
        message_channel_id = body["channel_id"]
        client = SlackApi(client=context["client"])
        channel_id = ba.join_channel(client, team_id, message_channel_id)
        if channel_id is None:
            ba.send_slack_message(
                channel_id=message_channel_id,
                text='Noe gikk galt. Klarte ikke å sette Pizza kanal',
                slack_client=client
            )
        else:
            ba.send_slack_message(
                channel_id=channel_id,
                text='Pizza kanal er nå satt til <#%s>' % channel_id,
                slack_client=client
            )


# This only exists to make bolt not throw a warning that we dont handle the file_shared event
# We dont use this as we use the message event with subtype file_shared as that one
# contains a full file object with url_private, while this one only contains the ID
# Perhaps another file event contains the full object?
def handle_file_shared_events(body):
    pass
