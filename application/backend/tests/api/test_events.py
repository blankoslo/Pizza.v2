import pytest
from flask import url_for


@pytest.mark.usefixtures('client_class')
class TestEventsSuit:
    def test_events_get(self):
        assert self.client.get(url_for('api.events.Events', method='get')).status_code == 401
