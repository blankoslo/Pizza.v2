import pytest
import uuid
from flask import url_for
from flask_jwt_extended import create_access_token
from tests.utils import assert_images

@pytest.mark.usefixtures('client_class')
class TestImagesSuit:
    def test_images_get(self, slack_organizations, users, images):
        user = users.get(slack_organizations[0].team_id)
        images = images.get(user.slack_organization_id)

        token = create_access_token(identity=user)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get(url_for('api.images.Images', method='get'), headers=headers)
        response_data = response.get_json()
        assert response.status_code == 200
        assert len(response_data) == 1
        assert_images(response_images=response_data, images=images)
