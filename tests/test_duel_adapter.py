from playerstars_graphql_adapters import DuelAdapter
from tests.basic_adapter_utils import api_id, api_key, aws_region


def test_duel_adapter():
    adapter = DuelAdapter(api_id, api_key, aws_region)
    assert adapter
