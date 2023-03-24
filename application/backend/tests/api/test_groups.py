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

    def test_groups_post_empty_members(self, slack_organizations, users):
        user = users.get(slack_organizations[0].team_id)

        token = create_access_token(identity=user)
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            'name': "dontCareName",
            'members': []
        }
        response = self.client.post(url_for('api.groups.Groups', method='post'), headers=headers, json=payload)
        assert response.status_code == 201

    def test_groups_post_with_members(self, slack_organizations, slack_users, users):
        user = users.get(slack_organizations[0].team_id)

        token = create_access_token(identity=user)
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            'name': "dontCareName",
            'members': [slack_users.get(slack_organizations[0].team_id)[0].slack_id]
        }
        response = self.client.post(url_for('api.groups.Groups', method='post'), headers=headers, json=payload)
        assert response.status_code == 201

    def test_groups_post_with_member_not_owned(self, slack_organizations, slack_users, users):
        user = users.get(slack_organizations[0].team_id)

        token = create_access_token(identity=user)
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            'name': "dontCareName",
            'members': [slack_users.get(slack_organizations[1].team_id)[0].slack_id]
        }
        response = self.client.post(url_for('api.groups.Groups', method='post'), headers=headers, json=payload)
        assert response.status_code == 400
