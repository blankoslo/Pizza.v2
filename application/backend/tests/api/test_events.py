import pytest
from flask import url_for
from flask_jwt_extended import create_access_token


@pytest.mark.usefixtures('client_class')
class TestEventsSuit:
    def test_events_get(self, user, events):
        token = create_access_token(identity=user)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get(url_for('api.events.Events', method='get'), headers=headers)
        response_data = response.get_json()
        expected_keys = ['id', 'restaurant', 'time', 'finalized', 'group', 'group_id', 'people_per_event']
        assert response.status_code == 200
        assert len(response_data) == 2
        assert all(set(expected_keys) == set(d.keys()) for d in response_data)


    def test_events_post(self, user):
        pass

    def test_events_by_id_get(self, user):
        pass

    def test_events_by_id_patch(self, user):
        pass

    def test_events_by_id_delete(self, user):
        pass
