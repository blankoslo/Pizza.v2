import pytest
from flask import url_for
from flask_jwt_extended import create_access_token


@pytest.mark.usefixtures('client_class')
class TestEventsSuit:
    def test_events_get(self, user):
        token = create_access_token(identity=user)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get(url_for('api.events.Events', method='get'), headers=headers)
        assert response.status_code == 200
