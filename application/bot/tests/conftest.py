import pytest


@pytest.fixture(autouse=True)
def environment_variables(monkeypatch):
    monkeypatch.setenv('SLACK_SIGNING_SECRET', 'dontCareSlackSigningSecret')
    monkeypatch.setenv('SLACK_CLIENT_ID', 'dontCareSlackClientId')
    monkeypatch.setenv('SLACK_CLIENT_SECRET', 'dontCareSlackClientSecret')
    monkeypatch.setenv('SLACK_APP_TOKEN', 'dontCareSlackAppToken')


@pytest.fixture(autouse=True)
def mock_injector(mocker, environment_variables):
    mock = mocker.MagicMock()
    mocker.patch('src.slack.handlers.injector', mock)
    return mock
