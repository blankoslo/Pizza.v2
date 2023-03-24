import pytest
from flask import url_for
from flask_jwt_extended import create_access_token
from tests.utils import assert_groups


@pytest.mark.usefixtures('client_class')
class TestGroupsSuit:
    def test_groups_get(self, slack_organizations, users, groups):
        user = users.get(slack_organizations[0].team_id)
        groups = groups.get(slack_organizations[0].team_id)

        token = create_access_token(identity=user)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get(url_for('api.groups.Groups', method='get'), headers=headers)
        response_data = response.get_json()
        assert response.status_code == 200
        assert len(response_data) == 1
        assert_groups(response_groups=response_data, groups=groups)
