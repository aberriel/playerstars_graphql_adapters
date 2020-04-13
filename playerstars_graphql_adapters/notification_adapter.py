from playerstars_graphql_adapters.basic_adapter import (
    BasicGraphqlAdapter)


class NotificationAdapter(BasicGraphqlAdapter):
    def __init__(self, api_id,
                 api_key,
                 aws_region,
                 object_name='Notification'):
        super(NotificationAdapter, self).__init__(
            api_id=api_id,
            api_key=api_key,
            aws_region=aws_region,
            object_name=object_name)
