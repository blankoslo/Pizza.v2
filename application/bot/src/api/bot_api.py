#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytz
import src.api.slack as slack
import src.database.interface as db
from datetime import datetime, timedelta
from src.database.rsvp import RSVP
from src.broker.AmqpConnection import AmqpConnection
from injector import inject, noninjectable

from src.broker.ApiClient import ApiClient

class BotApiConfiguration:
    def __init__(self, pizza_channel_id, timezone):
        self.pizza_channel_id = pizza_channel_id
        self.timezone = timezone

class BotApi:
    PEOPLE_PER_EVENT = 5
    REPLY_DEADLINE_IN_HOURS = 24
    DAYS_IN_ADVANCE_TO_INVITE = 10
    HOURS_BETWEEN_REMINDERS = 4

    @inject
    def __init__(self, mq: AmqpConnection, config: BotApiConfiguration):
        self.mq = mq
        self.pizza_channel_id = config.pizza_channel_id
        self.timezone = config.timezone
        self.client = ApiClient()

    def invite_multiple_if_needed(self):
        events = self.client.get_events_in_need_of_invitations(self.DAYS_IN_ADVANCE_TO_INVITE, self.PEOPLE_PER_EVENT)
        for event in events:
            self.invite_if_needed(event)

    def invite_if_needed(self, event):
        if event is None:
            print("No users were invited")
            return

        # timestamp (timestamp) is converted to UTC timestamp by psycopg2
        # Convert timestamp to Norwegian timestamp
        timestamp = pytz.utc.localize(event['event_time'].replace(tzinfo=None), is_dst=None).astimezone(self.timezone)
        users = self.client.get_users()
        number_of_employees = len(users)
        number_to_invite = self.PEOPLE_PER_EVENT - event['number_of_already_invited']
        users_to_invite = self.client.get_users_to_invite(number_to_invite, event['event_id'], number_of_employees, self.PEOPLE_PER_EVENT)
        users_to_invite = [user['id'] for user in users_to_invite]

        if len(users_to_invite) == 0:
            print("Event in need of users, but noone to invite") # TODO: needs to be handled
            return

        was_created = self.client.create_invitations(users_to_invite, event['event_id'])
        if not was_created:
            print("Was unable to create invitations")
            return

        for user_id in users_to_invite:
            self.send_pizza_invite(user_id, str(event['event_id']), event['restaurant_name'], timestamp.strftime("%A %d. %B kl %H:%M"), self.REPLY_DEADLINE_IN_HOURS)
            print("%s was invited to event on %s" % (user_id, timestamp))

    def send_reminders(self):
        invitations = self.client.get_unanswered_invitations()

        for invitation in invitations:
            # all timestamps (such as reminded_at) gets converted to UTC
            # so comparing it to datetime.now in UTC is correct
            remind_timestamp = datetime.now(pytz.utc) + timedelta(hours =- self.HOURS_BETWEEN_REMINDERS)
            if invitation['reminded_at'] < remind_timestamp:
                slack.send_slack_message(invitation['slack_id'], "Hei du! Jeg hørte ikke noe mer? Er du gira?")
                was_updated = self.client.update_invitation(
                    invitation['slack_id'],
                    invitation['event_id'],
                    {
                        "reminded_at": datetime.now().isoformat()
                    }
                )
                if was_updated:
                    print("%s was reminded about an event." % invitation['slack_id'])
                else:
                    print("failed to update invitation")

    def finalize_event_if_complete(self):
        event = db.get_event_ready_to_finalize(self.PEOPLE_PER_EVENT)
        if event is None:
            print("No events ready to finalize")
        else:
            # timestamp (timestamp) is converted to UTC timestamp by psycopg2
            event_id, timestamp, restaurant_id = event
            restaurant = db.get_restaurant_name(restaurant_id)
            # Convert timestamp to Norwegian timestamp
            timestamp = pytz.utc.localize(timestamp.replace(tzinfo=None), is_dst=None).astimezone(self.timezone)
            slack_ids = ['<@%s>' % user for user in db.get_attending_users(event_id)]
            db.mark_event_as_finalized(event_id)
            ids_string = ", ".join(slack_ids)
            booker = slack_ids[0]
            payer = slack_ids[1] if len(slack_ids) > 1 else slack_ids[0]
            slack.send_slack_message(self.pizza_channel_id, "Halloi! %s! Dere skal spise 🍕 på %s, %s. %s booker bord, og %s legger ut for maten. Blank betaler!" % (ids_string, restaurant, timestamp.strftime("%A %d. %B kl %H:%M"), booker, payer))

    def auto_reply(self):
        invitations = self.client.get_unanswered_invitations()

        for invitation in invitations:
            deadline = invitation['invited_at'] + timedelta(hours=self.REPLY_DEADLINE_IN_HOURS)
            if deadline < datetime.now(pytz.utc):
                was_updated = self.client.update_invitation(
                    invitation['slack_id'],
                    invitation['event_id'],
                    {
                        "rsvp": RSVP.not_attending
                    }
                )
                if was_updated:
                    slack.send_slack_message(invitation['slack_id'], "Neivel, da antar jeg du ikke kan/gidder. Håper du blir med neste gang! 🤞")
                    print("%s didn't answer. Setting RSVP to not attending." % invitation['slack_id'])
                else:
                    print("failed to update invitation to not attending")

    def save_image(self, cloudinary_id, slack_id, title):
        db.save_image(cloudinary_id, slack_id, title)

    def rsvp(self, slack_id, answer):
        db.rsvp(slack_id, answer)

    def accept_invitation(self, event_id, slack_id):
        db.update_invitation(event_id, slack_id, RSVP.attending)

    def decline_invitation(self, event_id, slack_id):
        db.update_invitation(event_id, slack_id, RSVP.not_attending)

    def withdraw_invitation(self, event_id, slack_id):
        in_past = db.event_in_past(event_id)
        if not in_past:
            db.update_invitation(event_id, slack_id, RSVP.not_attending)
            if db.event_is_finalized(event_id):
                db.mark_event_as_unfinalized(event_id)
        return in_past

    def send_slack_message_old(self, channel_id, text, attachments=None, thread_ts=None):
        return slack.send_slack_message_old(channel_id, text, attachments, thread_ts)

    def update_slack_message(self, channel_id, ts, text=None, blocks=None):
        return slack.update_slack_message(channel_id, ts, text, blocks)

    def send_pizza_invite(self, channel_id, event_id, place, datetime, deadline):
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Pizzainvitasjon"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": f"Du er invitert til :pizza: på {place}, {datetime}. Pls svar innen {deadline} timer :pray:. Kan du?"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Hells yesss!!! 🍕🍕🍕"
                        },
                        "value": event_id,
                        "action_id": "rsvp_yes",
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Nah ☹️"
                        },
                        "value": event_id,
                        "action_id": "rsvp_no",
                    }
                ]
            }
        ]
        return slack.send_slack_message(channel_id=channel_id, blocks=blocks)

    def clean_blocks(self, blocks):
        for block in blocks:
            del block["block_id"]
            if "text" in block and "emoji" in block["text"]:
                del block["text"]["emoji"]
        return blocks

    def send_pizza_invite_answered(self, channel_id, ts, event_id, old_blocks, attending):
        old_blocks = self.clean_blocks(old_blocks)
        new_blocks_common = [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": f"Du har takket {'ja. Sweet! 🤙' if attending else 'nei. Ok 😕'}",
                }
            }
        ]
        new_blocks_yes = [
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hvis noe skulle skje så kan du melde deg av ved å klikke på knappen!"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Meld meg av"
                    },
                    "value": event_id,
                    "action_id": "rsvp_withdraw"
                }
            }
        ]
        blocks = old_blocks + new_blocks_common
        if attending:
            blocks += new_blocks_yes
        return slack.update_slack_message(channel_id=channel_id, ts=ts, blocks=blocks)

    def send_pizza_invite_withdraw(self, channel_id, ts, old_blocks):
        old_blocks = self.clean_blocks(old_blocks)
        new_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "Du har meldt deg av. Ok 😕",
                }
            }
        ]
        blocks = old_blocks + new_blocks
        return slack.update_slack_message(channel_id=channel_id, ts=ts, blocks=blocks)

    def send_pizza_invite_withdraw_failure(self, channel_id, ts, old_blocks):
        old_blocks = self.clean_blocks(old_blocks)
        new_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "Pizza arrangementet er over. Avmelding er ikke mulig.",
                }
            }
        ]
        blocks = old_blocks + new_blocks
        return slack.update_slack_message(channel_id=channel_id, ts=ts, blocks=blocks)

    def get_invited_users(self):
        return db.get_invited_users()

    def sync_db_with_slack_and_return_count(self):
      all_slack_users = slack.get_slack_users()
      slack_users = slack.get_real_users(all_slack_users)
      db.update_slack_users(slack_users)
      return len(slack_users)
