from playerstars_graphql_adapters.basic_graphql_adapter import (
    BasicGraphqlAdapter)


class NotificationAdapter(BasicGraphqlAdapter):
    def __init__(self, object_name='Notification'):
        super(NotificationAdapter, self).__init__(object_name=object_name)
