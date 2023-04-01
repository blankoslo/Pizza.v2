import pytest
from flask_jwt_extended import create_refresh_token, decode_token


@pytest.mark.usefixtures('client_class')
class TestAuthSuit:
    def test_refresh(self, slack_organizations, users, ):
        user = users.get(slack_organizations[0].team_id)

        token = create_refresh_token(identity=user)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post('/api/auth/refresh', method='post', headers=headers)
        decoded_token = decode_token(response.get_json()['access_token'])
        assert response.status_code == 200
        assert decoded_token['user']['id'] == user.id

    def test_login(self):
        response = self.client.get('/api/auth/login', method='get')
        response_data = response.get_json()
        auth_url = response_data['auth_url']
        assert response.status_code == 200
        assert isinstance(auth_url, str)

    def test_login_callback(self):
        pass
