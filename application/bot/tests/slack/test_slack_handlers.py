import pytest
import logging

@pytest.fixture
def mock_bot_api(mocker, mock_injector, environment_variables):
    mock = mocker.MagicMock()
    mocker.patch('src.slack.handlers.BotApi', mock)
    yield mock
    mock.reset_mock()


@pytest.fixture
def mock_injected_bot_api(mocker, mock_bot_api, mock_injector):
    mock_bot_api_instance = mocker.MagicMock()
    def side_effect(inject_class):
        print(mock_bot_api, inject_class, mock_bot_api == inject_class)
        if mock_bot_api == inject_class:
            return mock_bot_api_instance
        elif logging.Logger == inject_class:
            return mocker.MagicMock()
        return None
    mock_injector.get.side_effect = side_effect
    return mock_bot_api_instance


@pytest.fixture
def mock_injected_entered_bot_api(mocker, mock_injected_bot_api):
    mock_injected_bot_api_entered = mocker.MagicMock()
    mock_injected_bot_api.__enter__.return_value = mock_injected_bot_api_entered
    return mock_injected_bot_api_entered


@pytest.fixture(autouse=True)
def mock_slack_api(mocker, environment_variables):
    mock = mocker.MagicMock()
    mocker.patch('src.slack.handlers.SlackApi', mock)
    return mock


@pytest.fixture
def mocked_requests(mocker):
    post_mock = mocker.MagicMock()
    mocker.patch("requests.post", post_mock)
    get_mock = mocker.MagicMock()
    mocker.patch("requests.get", get_mock)
    yield post_mock, get_mock


class TestSlackHandlersSuit:
    def test_handle_event(self, mocker, mocked_requests, mock_injected_entered_bot_api):
        from src.slack.handlers import handle_message_event

        post_mock, get_mock = mocked_requests
        type(get_mock.return_value).content = mocker.PropertyMock(return_value=b"dontCare")

        body = {'event': {
            'subtype': 'file_share',
            'channel': 'dontCareChannelId',
            'files': [
                {
                    'url_private': 'dontCareUrl',
                    'user_team': 'dontCareTeam',
                    'user': 'dontCareUser',
                    'title': 'dontCareTitle'
                }
            ]
        }}
        ack = mocker.MagicMock()
        context = {
            'token': "dontCareToken",
            'client': mocker.MagicMock()
        }

        handle_message_event(ack=ack, body=body, context=context)

        mock_injected_entered_bot_api.send_slack_message.assert_called_once()
        get_mock.assert_called_once()
        post_mock.assert_called_once()
        mock_injected_entered_bot_api.save_image.assert_called_once()

    def test_handle_rsvp_yes_user_not_among_invited(self, mocker, mock_injected_bot_api, mock_injected_entered_bot_api):
        from src.slack.handlers import handle_rsvp_yes

        body = {
            'user': {
                'id': 'userId'
            },
            'channel': {
                'id': 'channelId',
            },
            'message': {
                'ts': 'message_ts',
                'blocks': [
                    mocker.MagicMock(),
                    mocker.MagicMock(),
                    mocker.MagicMock(),
                ]
            },
            'actions': [
                {
                    'value': 'event_id'
                }
            ]
        }
        ack = mocker.MagicMock()
        context = {
            'client': mocker.MagicMock()
        }

        mock_injected_entered_bot_api.get_invited_users.return_value = []

        handle_rsvp_yes(ack=ack, body=body, context=context)

        mock_injected_bot_api.send_pizza_invite_loading.assert_called_once()
        ack.assert_called_once()
        mock_injected_entered_bot_api.get_invited_users.assert_called_once()
        mock_injected_entered_bot_api.send_pizza_invite_not_among_invited_users.assert_called_once()

    def test_handle_rsvp_yes(self, mocker, mock_injected_bot_api, mock_injected_entered_bot_api):
        from src.slack.handlers import handle_rsvp_yes

        body = {
            'user': {
                'id': 'userId'
            },
            'channel': {
                'id': 'channelId',
            },
            'message': {
                'ts': 'message_ts',
                'blocks': [
                    mocker.MagicMock(),
                    mocker.MagicMock(),
                    mocker.MagicMock(),
                ]
            },
            'actions': [
                {
                    'value': 'event_id'
                }
            ]
        }
        ack = mocker.MagicMock()
        context = {
            'client': mocker.MagicMock()
        }

        mock_injected_entered_bot_api.get_invited_users.return_value = ['userId']

        handle_rsvp_yes(ack=ack, body=body, context=context)

        mock_injected_bot_api.send_pizza_invite_loading.assert_called_once()
        ack.assert_called_once()
        mock_injected_entered_bot_api.get_invited_users.assert_called_once()
        mock_injected_entered_bot_api.accept_invitation.assert_called_once()
        mock_injected_entered_bot_api.send_pizza_invite_answered.assert_called_once()

    def test_handle_rsvp_no_user_not_among_invited(self, mocker, mock_injected_bot_api, mock_injected_entered_bot_api):
        from src.slack.handlers import handle_rsvp_no

        body = {
            'user': {
                'id': 'userId'
            },
            'channel': {
                'id': 'channelId',
            },
            'message': {
                'ts': 'message_ts',
                'blocks': [
                    mocker.MagicMock(),
                    mocker.MagicMock(),
                    mocker.MagicMock(),
                ]
            },
            'actions': [
                {
                    'value': 'event_id'
                }
            ]
        }
        ack = mocker.MagicMock()
        context = {
            'client': mocker.MagicMock()
        }

        mock_injected_entered_bot_api.get_invited_users.return_value = []

        handle_rsvp_no(ack=ack, body=body, context=context)

        mock_injected_bot_api.send_pizza_invite_loading.assert_called_once()
        ack.assert_called_once()
        mock_injected_entered_bot_api.get_invited_users.assert_called_once()
        mock_injected_entered_bot_api.send_pizza_invite_not_among_invited_users.assert_called_once()

    def test_handle_rsvp_no(self, mocker, mock_injected_bot_api, mock_injected_entered_bot_api):
        from src.slack.handlers import handle_rsvp_no

        body = {
            'user': {
                'id': 'userId'
            },
            'channel': {
                'id': 'channelId',
            },
            'message': {
                'ts': 'message_ts',
                'blocks': [
                    mocker.MagicMock(),
                    mocker.MagicMock(),
                    mocker.MagicMock(),
                ]
            },
            'actions': [
                {
                    'value': 'event_id'
                }
            ]
        }
        ack = mocker.MagicMock()
        context = {
            'client': mocker.MagicMock()
        }

        mock_injected_entered_bot_api.get_invited_users.return_value = ['userId']

        handle_rsvp_no(ack=ack, body=body, context=context)

        mock_injected_bot_api.send_pizza_invite_loading.assert_called_once()
        ack.assert_called_once()
        mock_injected_entered_bot_api.get_invited_users.assert_called_once()
        mock_injected_entered_bot_api.decline_invitation.assert_called_once()
        mock_injected_entered_bot_api.invite_multiple_if_needed.assert_called_once()
        mock_injected_entered_bot_api.send_pizza_invite_answered.assert_called_once()

    def test_handle_rsvp_withdraw_success(self, mocker, mock_injected_bot_api, mock_injected_entered_bot_api):
        from src.slack.handlers import handle_rsvp_withdraw

        body = {
            'user': {
                'id': 'userId'
            },
            'channel': {
                'id': 'channelId',
            },
            'message': {
                'ts': 'message_ts',
                'blocks': [
                    mocker.MagicMock(),
                    mocker.MagicMock(),
                    mocker.MagicMock(),
                ]
            },
            'actions': [
                {
                    'value': 'event_id'
                }
            ]
        }
        ack = mocker.MagicMock()
        context = {
            'client': mocker.MagicMock()
        }

        mock_injected_entered_bot_api.withdraw_invitation.return_value = True

        handle_rsvp_withdraw(ack=ack, body=body, context=context)

        mock_injected_bot_api.send_pizza_invite_loading.assert_called_once()
        ack.assert_called_once()
        mock_injected_entered_bot_api.withdraw_invitation.assert_called_once()
        mock_injected_entered_bot_api.send_pizza_invite_withdraw.assert_called_once()

    def test_handle_rsvp_withdraw_failure(self, mocker, mock_injected_bot_api, mock_injected_entered_bot_api):
        from src.slack.handlers import handle_rsvp_withdraw

        body = {
            'user': {
                'id': 'userId'
            },
            'channel': {
                'id': 'channelId',
            },
            'message': {
                'ts': 'message_ts',
                'blocks': [
                    mocker.MagicMock(),
                    mocker.MagicMock(),
                    mocker.MagicMock(),
                ]
            },
            'actions': [
                {
                    'value': 'event_id'
                }
            ]
        }
        ack = mocker.MagicMock()
        context = {
            'client': mocker.MagicMock()
        }

        mock_injected_entered_bot_api.withdraw_invitation.return_value = False

        handle_rsvp_withdraw(ack=ack, body=body, context=context)

        mock_injected_bot_api.send_pizza_invite_loading.assert_called_once()
        ack.assert_called_once()
        mock_injected_entered_bot_api.withdraw_invitation.assert_called_once()
        mock_injected_entered_bot_api.send_pizza_invite_withdraw_failure.assert_called_once()

    def test_handle_set_channel_command_success(self, mocker, mock_injected_entered_bot_api):
        from src.slack.handlers import handle_set_channel_command

        body = {
            'team_id': 'someTeamId',
            'channel_id': 'someChannelId',
        }
        ack = mocker.MagicMock()
        context = {
            'client': mocker.MagicMock()
        }

        mock_injected_entered_bot_api.join_channel.return_value = 'someNewChannel'

        handle_set_channel_command(ack=ack, body=body, context=context)

        ack.assert_called_once()
        mock_injected_entered_bot_api.join_channel.assert_called_once()
        mock_injected_entered_bot_api.send_slack_message.assert_called_once()
        assert len(mock_injected_entered_bot_api.send_slack_message.call_args_list) == 1
        print(mock_injected_entered_bot_api.send_slack_message.call_args_list[0].kwargs)
        assert mock_injected_entered_bot_api.send_slack_message.call_args_list[0].kwargs['channel_id'] == 'someNewChannel'

    def test_handle_set_channel_command_failure(self, mocker, mock_injected_entered_bot_api):
        from src.slack.handlers import handle_set_channel_command

        body = {
            'team_id': 'someTeamId',
            'channel_id': 'someChannelId',
        }
        ack = mocker.MagicMock()
        context = {
            'client': mocker.MagicMock()
        }

        mock_injected_entered_bot_api.join_channel.return_value = None

        handle_set_channel_command(ack=ack, body=body, context=context)

        ack.assert_called_once()
        mock_injected_entered_bot_api.join_channel.assert_called_once()
        mock_injected_entered_bot_api.send_slack_message.assert_called_once()
        assert len(mock_injected_entered_bot_api.send_slack_message.call_args_list) == 1
        print(mock_injected_entered_bot_api.send_slack_message.call_args_list[0].kwargs)
        assert mock_injected_entered_bot_api.send_slack_message.call_args_list[0].kwargs['channel_id'] == 'someChannelId'


