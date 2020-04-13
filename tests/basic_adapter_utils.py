from datetime import datetime
from enum import Enum
from marshmallow import fields, post_load
from playerstars_adapters import BasicGraphqlAdapter
from playerstars_domain import (
    BasicEntity,
    BasicValue)
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

        @post_load
        def post_load(self, data, many, partial, **kwargs):
            return Telephone(**data)


class Person(BasicEntity):
    def __init__(self,
                 name: str,
                 telephone: Telephone,
                 creation_datetime: datetime = None,
                 contact_type: ContactType = ContactType.OTHER,
                 comments: str = None,
                 entity_id: str = None):
        super(Person, self).__init__(entity_id=entity_id)
        self.name = name
        self.telephone = telephone
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
        comments = fields.String(required=False, allow_none=True)

        @post_load
        def post_load(self, data, many, partial, **kwargs):
            return Person(**data)


class PersonAdapter(BasicGraphqlAdapter):
    def __init__(self, api_id, api_key, aws_region, object_name='Person'):
        super(PersonAdapter, self).__init__(
            api_id=api_id,
            api_key=api_key,
            aws_region=aws_region,
            object_name=object_name)
