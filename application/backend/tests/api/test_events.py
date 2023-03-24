import pytest
from flask import url_for
from flask_jwt_extended import create_access_token
from pymaybe import maybe


@pytest.mark.usefixtures('client_class')
class TestEventsSuit:
    def test_events_get(self, slack_organizations, users, events):
        user = users.get(slack_organizations[0].team_id)
        events = events.get(user.slack_organization_id)

        token = create_access_token(identity=user)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get(url_for('api.events.Events', method='get'), headers=headers)
        response_data = response.get_json()
        expected_keys = ['id', 'restaurant', 'time', 'finalized', 'group', 'group_id', 'people_per_event']
        assert response.status_code == 200
        assert len(response_data) == 2
        assert all(set(expected_keys) == set(d.keys()) for d in response_data)

        events_sorted = sorted(events, key=lambda x: x.id)
        response_data_sorted = sorted(response_data, key=lambda x: x['id'])
        for i, event in enumerate(events_sorted):
            # simple fields
            assert response_data_sorted[i]["id"] == str(event.id)
            assert response_data_sorted[i]["time"] == event.time.isoformat()
            assert response_data_sorted[i]["finalized"] == event.finalized
            assert response_data_sorted[i]["group_id"] == (str(event.group_id) if event.group_id is not None else None)
            assert response_data_sorted[i]["people_per_event"] == event.people_per_event
            # ******* Relations *******
            # restaurant
            expected_restaurant_keys = ["id", "name", "link", "tlf", "address", "rating"]
            assert set(expected_restaurant_keys) == set(response_data_sorted[i]["restaurant"].keys())
            assert response_data_sorted[i]["restaurant"]['id'] == str(event.restaurant.id)
            assert response_data_sorted[i]["restaurant"]['name'] == event.restaurant.name
            assert response_data_sorted[i]["restaurant"]['link'] == event.restaurant.link
            assert response_data_sorted[i]["restaurant"]['tlf'] == event.restaurant.tlf
            assert response_data_sorted[i]["restaurant"]['address'] == event.restaurant.address
            assert response_data_sorted[i]["restaurant"]['rating'] == event.restaurant.rating
            # group
            assert maybe(response_data_sorted[i]["group"])["id"] == maybe(str(event.group.id) if event.group is not None else None)
            assert maybe(response_data_sorted[i]["group"])["name"] == maybe(event.group).name
            if response_data_sorted[i]["group"] is not None:
                expected_restaurant_keys = ["id", "name", "members"]
                assert set(expected_restaurant_keys) == set(response_data_sorted[i]["group"].keys())

                # members in group
                members_sorted = sorted(event.group.members, key=lambda x: x.slack_id)
                response_members_sorted = sorted(response_data_sorted[i]["group"]["members"], key=lambda x: x['slack_id'])
                for i, member in enumerate(members_sorted):
                    expected_restaurant_keys = ["slack_id", "current_username", "first_seen", "active", "priority", "email"]
                    assert set(expected_restaurant_keys) == set(response_members_sorted[i].keys())
                    assert response_members_sorted[i]["slack_id"] == str(member.slack_id)
                    assert response_members_sorted[i]["current_username"] == member.current_username
                    assert response_members_sorted[i]["first_seen"] == member.first_seen.isoformat()
                    assert response_members_sorted[i]["active"] == member.active
                    assert response_members_sorted[i]["priority"] == member.priority
                    assert response_members_sorted[i]["email"] == member.email

    def test_events_post_no_group(self, slack_organizations, users, restaurant):
        user = users.get(slack_organizations[0].team_id)

        token = create_access_token(identity=user)
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "restaurant_id": restaurant.get(user.slack_organization_id)[0].id,
            "time": "2023-03-28T16:23:05.420Z",
            "people_per_event": 5
        }
        response = self.client.post(url_for('api.events.Events', method='post'), headers=headers, json=payload)
        assert response.status_code == 201

    def test_events_post_group(self, slack_organizations, users, restaurant, groups):
        user = users.get(slack_organizations[0].team_id)

        token = create_access_token(identity=user)
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "restaurant_id": restaurant.get(user.slack_organization_id)[0].id,
            "group_id": groups.get(user.slack_organization_id)[0].id,
            "time": "2023-03-28T16:23:05.420Z",
            "people_per_event": 5
        }
        response = self.client.post(url_for('api.events.Events', method='post'), headers=headers, json=payload)
        assert response.status_code == 201

    def test_events_post_not_owned_restaurant(self, slack_organizations, users, restaurant):
        user = users.get(slack_organizations[0].team_id)

        token = create_access_token(identity=user)
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "restaurant_id": restaurant.get(slack_organizations[1].team_id)[0].id,
            "time": "2023-03-28T16:23:05.420Z",
            "people_per_event": 5
        }
        response = self.client.post(url_for('api.events.Events', method='post'), headers=headers, json=payload)
        assert response.status_code == 400

    def test_events_post_not_owned_group(self, slack_organizations, users, restaurant, groups):
        user = users.get(slack_organizations[0].team_id)

        token = create_access_token(identity=user)
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "restaurant_id": restaurant.get(user.slack_organization_id)[0].id,
            "time": "2023-03-28T16:23:05.420Z",
            "people_per_event": 5,
            "group_id": groups.get(slack_organizations[1].team_id)[0].id,
        }
        response = self.client.post(url_for('api.events.Events', method='post'), headers=headers, json=payload)
        assert response.status_code == 400

    def test_events_by_id_get(self, slack_organizations, users):
        user = users.get(slack_organizations[0].team_id)
        pass

    def test_events_by_id_patch(self, slack_organizations, users):
        user = users.get(slack_organizations[0].team_id)
        pass

    def test_events_by_id_delete(self, slack_organizations, users):
        user = users.get(slack_organizations[0].team_id)
        pass
