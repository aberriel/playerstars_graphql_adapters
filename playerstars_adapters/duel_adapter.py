from playerstars_adapters.basic_adapter import (
    BasicGraphqlAdapter)


class DuelAdapter(BasicGraphqlAdapter):
    def __init__(self, api_id, api_key, aws_region, object_name='Duel'):
        super(DuelAdapter, self).__init__(
            api_id=api_id,
            api_key=api_key,
            aws_region=aws_region,
            object_name=object_name)
