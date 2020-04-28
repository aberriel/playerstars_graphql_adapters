from datetime import datetime
from enum import Enum
from marshmallow import fields
from marshmallow_enum import EnumField
from playerstars_domain import (
    BasicEntity,
    BasicValue)


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
                 name,
                 telephone: Telephone,
                 address: str = None,
                 creation_datetime: datetime = None,
                 contact_type: ContactType = ContactType.OTHER,
                 comments: str = None,
                 entity_id: str = None):
        super(Person, self).__init__(entity_id=entity_id)
        self.name = name
        self.telephone = telephone
        self.address = address
        self.contact_type = contact_type
        self.comments = comments
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
        address = fields.String(
            required=False,
            allow_none=True,
            default='default address')
        comments = fields.String(required=False, allow_none=True)


person_creation_datetime = datetime(2020, 4, 13, 15, 42, 6, 88967)
api_url = 'api_url'
api_id = 'api_id'
api_key = 'api_key'
aws_region = 'aws_region'


person_attribute_list = {
    'contact_type': {
        'name': 'contact_type',
        'type': ContactType,
        'is_required': True,
        'allow_none': False,
        'is_custom': False,
        'value': ContactType.CLIENT
    },
    'creation_datetime': {
        'name': 'creation_datetime',
        'type': datetime,
        'is_required': True,
        'allow_none': False,
        'is_custom': False,
        'value': person_creation_datetime
    },
    'entity_id': {
        'name': 'entity_id',
        'type': str,
        'is_required': True,
        'allow_none': False,
        'is_custom': False,
        'value': 'person123'
    },
    'name': {
        'name': 'name',
        'type': str,
        'is_required': True,
        'allow_none': False,
        'is_custom': False,
        'value': 'Anselmo Lira'
    },
    'address': {
        'name': 'address',
        'type': str,
        'is_required': False,
        'allow_none': True,
        'is_custom': False,
        'value': 'default address'
    },
    'telephone': {
        'name': 'telephone',
        'type': Telephone,
        'is_required': False,
        'allow_none': True,
        'is_custom': True,
        'value': {
            'country_code': {
                'name': 'country_code',
                'type': str,
                'is_required': True,
                'allow_none': False,
                'is_custom': False,
                'value': '55'
            },
            'local_code': {
                'name': 'local_code',
                'type': str,
                'is_required': True,
                'allow_none': False,
                'is_custom': False,
                'value': '21'
            },
            'number': {
                'name': 'number',
                'type': str,
                'is_required': True,
                'allow_none': False,
                'is_custom': False,
                'value': '99144-1522'
            }
        }
    }
}
