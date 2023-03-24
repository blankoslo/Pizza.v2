import pytest
from flask import url_for
from flask_jwt_extended import create_access_token
from pymaybe import maybe


@pytest.mark.usefixtures('client_class')
class TestEventsSuit:
    def _assert_event(self, response_events, events):
        expected_keys = ['id', 'restaurant', 'time', 'finalized', 'group', 'group_id', 'people_per_event']
        assert all(set(expected_keys) == set(d.keys()) for d in response_events)

        events_sorted = sorted(events, key=lambda x: x.id)
        response_events_sorted = sorted(response_events, key=lambda x: x['id'])
        for i, event in enumerate(events_sorted):
            response_event = response_events_sorted[i]
            # simple fields
            assert response_event["id"] == str(event.id)
            assert response_event["time"] == event.time.isoformat()
            assert response_event["finalized"] == event.finalized
            assert response_event["group_id"] == (str(event.group_id) if event.group_id is not None else None)
            assert response_event["people_per_event"] == event.people_per_event
            # ******* Relations *******
            # restaurant
            expected_restaurant_keys = ["id", "name", "link", "tlf", "address", "rating"]
            assert set(expected_restaurant_keys) == set(response_event["restaurant"].keys())
            assert response_event["restaurant"]['id'] == str(event.restaurant.id)
            assert response_event["restaurant"]['name'] == event.restaurant.name
            assert response_event["restaurant"]['link'] == event.restaurant.link
            assert response_event["restaurant"]['tlf'] == event.restaurant.tlf
            assert response_event["restaurant"]['address'] == event.restaurant.address
            assert response_event["restaurant"]['rating'] == event.restaurant.rating
            # group
            assert maybe(response_event["group"])["id"] == maybe(str(event.group.id) if event.group is not None else None)
            assert maybe(response_event["group"])["name"] == maybe(event.group).name
            if response_event["group"] is not None:
                expected_restaurant_keys = ["id", "name", "members"]
                assert set(expected_restaurant_keys) == set(response_event["group"].keys())

                # members in group
                members_sorted = sorted(event.group.members, key=lambda x: x.slack_id)
                response_members_sorted = sorted(response_event["group"]["members"], key=lambda x: x['slack_id'])
                for i, member in enumerate(members_sorted):
                    expected_restaurant_keys = ["slack_id", "current_username", "first_seen", "active", "priority", "email"]
                    assert set(expected_restaurant_keys) == set(response_members_sorted[i].keys())
                    assert response_members_sorted[i]["slack_id"] == str(member.slack_id)
                    assert response_members_sorted[i]["current_username"] == member.current_username
                    assert response_members_sorted[i]["first_seen"] == member.first_seen.isoformat()
                    assert response_members_sorted[i]["active"] == member.active
                    assert response_members_sorted[i]["priority"] == member.priority
                    assert response_members_sorted[i]["email"] == member.email

    def test_events_get(self, slack_organizations, users, events):
        user = users.get(slack_organizations[0].team_id)
        events = events.get(user.slack_organization_id)

        token = create_access_token(identity=user)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get(url_for('api.events.Events', method='get'), headers=headers)
        response_data = response.get_json()
        assert response.status_code == 200
        assert len(response_data) == 2
        self._assert_event(response_events=response_data, events=events)


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

    def test_events_by_id_get(self, slack_organizations, users, events):
        user = users.get(slack_organizations[0].team_id)
        event = events.get(slack_organizations[0].team_id)[0]

        token = create_access_token(identity=user)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get(url_for('api.events.EventsById', method='get', event_id=event.id), headers=headers)
        response_data = response.get_json()
        assert response.status_code == 200
        self._assert_event([response_data], [event])

    def test_events_by_id_get_not_owned(self, slack_organizations, users, events):
        user = users.get(slack_organizations[0].team_id)
        event = events.get(slack_organizations[1].team_id)[0]

        token = create_access_token(identity=user)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get(url_for('api.events.EventsById', method='get', event_id=event.id), headers=headers)
        assert response.status_code == 404

    def test_events_by_id_patch(self, slack_organizations, users):
        user = users.get(slack_organizations[0].team_id)
        pass

    def test_events_by_id_patch_not_owned(self, slack_organizations, users):
        user = users.get(slack_organizations[0].team_id)
        pass

    def test_events_by_id_delete(self, slack_organizations, users, events):
        user = users.get(slack_organizations[0].team_id)
        event = events.get(slack_organizations[0].team_id)[0]

        token = create_access_token(identity=user)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.delete(url_for('api.events.EventsById', method='delete', event_id=event.id), headers=headers)
        assert response.status_code == 204

    def test_events_by_id_delete_not_owned(self, slack_organizations, users, events):
        user = users.get(slack_organizations[0].team_id)
        event = events.get(slack_organizations[1].team_id)[0]

        token = create_access_token(identity=user)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.delete(url_for('api.events.EventsById', method='delete', event_id=event.id), headers=headers)
        assert response.status_code == 400
