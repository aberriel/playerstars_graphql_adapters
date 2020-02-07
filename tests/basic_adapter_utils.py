from marshmallow import fields, post_load
from playerstars_graphql_adapters import BasicGraphqlAdapter
from playerstars_domain import BasicEntity, Notification


class Patches:
    BASE = '',
    APP_SYNC_CLIENT = '',
    QUERY_MUTATION = '',
    OBJECT_ATTRIBUTE_LIST = ''


class TestEntity(BasicEntity):
    def __init__(self, name: str, telephone: str, entity_id: str = None):
        super(TestEntity, self).__init__(entity_id=entity_id)
        self.name = name
        self.telephone = telephone

    class Schema(BasicEntity.Schema):
        name = fields.String(required=True, allow_none=False)
        telephone = fields.String(required=False, allow_none=True)

        @post_load
        def post_load(self, data, many, partial):
            return TestEntity(**data)


class TestAdapter(BasicGraphqlAdapter):
    def __init__(self, api_id, api_key, aws_region, object_name):
        super(TestAdapter, self).__init__(
            api_id=api_id,
            api_key=api_key,
            aws_region=aws_region,
            object_name='Test')


app_sync_response = {
    'data': {
        'createNotification': {
            'creation_datetime': '2020-02-06T20:12:40.942472',
            'entity_id': '1685f4b1-83c9-40c5-a7df-aacf29575ce3',
            'notification_complement': 'Teste 7',
            'notification_type': 'INFORMATIVE',
            'player_id': '9b8c1e9c-a872-46f8-8c72-ed5677f0374c',
            'status': 'CREATED'
        }
    }
}


notification_data = Notification(
    player_id='9b8c1e9c-a872-46f8-8c72-ed5677f0374c',
    notification_complement='Teste 6')


notification_data_with_id = Notification(
    entity_id='1685f4b1-83c9-40c5-a7df-aacf29575ce3',
    player_id='9b8c1e9c-a872-46f8-8c72-ed5677f0374c',
    notification_complement='Teste 6')
