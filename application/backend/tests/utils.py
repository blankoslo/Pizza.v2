from pymaybe import maybe

def assert_events(response_events, events):
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
            assert_groups(response_groups=[response_event["group"]], groups=[event.group])


def assert_groups(response_groups, groups):
    expected_keys = ['id', 'name', 'members']
    assert all(set(expected_keys) == set(d.keys()) for d in response_groups)

    groups_sorted = sorted(groups, key=lambda x: x.id)
    response_groups_sorted = sorted(response_groups, key=lambda x: x['id'])
    for i, group in enumerate(groups_sorted):
        response_group = response_groups_sorted[i]
        # simple fields
        assert response_group["id"] == str(group.id)
        assert response_group["name"] == group.name

        # members in group
        assert_slack_user(response_slack_users=response_group["members"], slack_users=group.members)


def assert_slack_user(response_slack_users, slack_users):
    expected_slack_users_keys = ["slack_id", "current_username", "first_seen", "active", "priority", "email"]
    assert all(set(expected_slack_users_keys) == set(d.keys()) for d in response_slack_users)

    members_sorted = sorted(slack_users, key=lambda x: x.slack_id)
    response_members_sorted = sorted(response_slack_users, key=lambda x: x['slack_id'])
    for i, member in enumerate(members_sorted):
        assert response_members_sorted[i]["slack_id"] == str(member.slack_id)
        assert response_members_sorted[i]["current_username"] == member.current_username
        assert response_members_sorted[i]["first_seen"] == member.first_seen.isoformat()
        assert response_members_sorted[i]["active"] == member.active
        assert response_members_sorted[i]["priority"] == member.priority
        assert response_members_sorted[i]["email"] == member.email
