from playerstars_graphql_adapters import NotificationAdapter
from tests.basic_adapter_utils import api_id, api_key, aws_region


def test_notification_adapter():
    adapter = NotificationAdapter(api_id, api_key, aws_region)
    assert adapter
