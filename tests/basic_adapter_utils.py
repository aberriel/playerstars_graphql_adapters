from datetime import datetime
from enum import Enum
from marshmallow import fields, post_load
from playerstars_adapters import BasicGraphqlAdapter
from playerstars_domain import (
    BasicEntity,
    BasicValue,
    Notification
)
from playerstars_domain.utils.enum_field import EnumField


class ContactType(Enum):
    CLIENT = 'client'
    FRIEND = 'friend'
    OTHER = 'other'


class Telephone(BasicValue):
    def __init__(self,
                 country_code: str,
                 local_code: str,
                 number: str):
        super(Telephone, self).__init__()
        self.country_code = country_code
        self.local_code = local_code
        self.number = number

    class Schema(BasicValue.Schema):
        country_code = fields.String(required=True, allow_none=False)
        local_code = fields.String(required=True, allow_none=False)
        number = fields.String(required=True, allow_none=False)


class Person(BasicEntity):
    def __init__(self,
                 name: str,
                 telephone: Telephone,
                 creation_datetime: datetime = None,
                 contact_type: ContactType = ContactType.OTHER,
                 entity_id: str = None):
        super(Person, self).__init__(entity_id=entity_id)
        self.name = name
        self.telephone = telephone
        self.contact_type = contact_type
        self.creation_datetime = creation_datetime or datetime.utcnow()

    class Schema(BasicEntity.Schema):
        name = fields.String(required=True, allow_none=False)
        telephone = fields.Nested(
            Telephone.Schema,
            required=False,
            allow_none=True)
        creation_datetime = fields.DateTime(
            format='iso',
            required=True,
            allow_none=False)
        contact_type = EnumField(
            ContactType,
            required=True,
            allow_none=False,
            default=ContactType.OTHER)

        @post_load
        def post_load(self, data, many, partial):
            return Person(**data)


class PersonAdapter(BasicGraphqlAdapter):
    def __init__(self, api_id, api_key, aws_region, object_name):
        super(PersonAdapter, self).__init__(
            api_id=api_id,
            api_key=api_key,
            aws_region=aws_region,
            object_name='Test')


app_sync_response_notification = {
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


app_sync_response_test_object = {
    'data': {
        'createTestObject': {
            'entity_id': 'aqswde1',
            'name': 'Anselmo',
            'telephone': '99991-1519'
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


test_telephone = Telephone(
    country_code='55',
    local_code='21',
    number='99991-1519')


test_object_data = Person(
    name='Anselmo',
    telephone=test_telephone,
    creation_datetime=datetime(2020, 2, 10, 15, 16, 17),
    contact_type=ContactType.FRIEND)


test_object_data_with_id = Person(
    name='Anselmo',
    telephone=test_telephone,
    creation_datetime=datetime(2020, 2, 10, 15, 16, 17),
    contact_type=ContactType.FRIEND,
    entity_id='aqswde1')
