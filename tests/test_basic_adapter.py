from .basic_adapter_utils import (
    ContactType,
    Person,
    PersonAdapter,
    Telephone)
from datetime import datetime
from playerstars_adapters import (
    BasicGraphqlAdapter)


def make_telephone_data():
    telephone = Telephone(
        country_code='55',
        local_code='21',
        number='99144-1522')
    return telephone


def make_person_data():
    telephone_data = make_telephone_data()
    person_data = Person(
        name='Anselmo Lira',
        telephone=telephone_data,
        contact_type=ContactType.CLIENT)
    return person_data


api_url = 'api_url'
api_id = 'api_id'
api_key = 'api_key'
aws_region = 'aws_region'


def test_basic_graphql_adapter():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    assert basic_adapter


def test_create_data_mutation():
    pass


def test_update_data_mutation():
    pass


def test_delete_data_mutation():
    pass


def test_search():
    pass


def test_save():
    pass


def test_delete():
    pass


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
        'value': datetime(2020, 4, 9, 23, 59, 59, 98331)
    },
    'entity_id': {
        'name': 'entity_id',
        'type': str,
        'is_required': True,
        'allow_none': False,
        'is_custom': False,
        'value': 'd7e95144-5a05-497f-96ab-e5df997955bd'
    },
    'name': {
        'name': 'name',
        'type': str,
        'is_required': True,
        'allow_none': False,
        'is_custom': False,
        'value': 'Anselmo Lira'
    },
    'telephone': {
        'name': 'telephone',
        'type': Telephone,
        'is_required': False,
        'allow_none': True,
        'is_custom': False,
        'value': make_telephone_data()
    }
}

def test_get_attribute_list():
    person_data = make_person_data()
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    attribute_list = basic_adapter.get_object_attribute_list(person_data)
    assert attribute_list
    assert isinstance(attribute_list, dict)
    assert attribute_list == person_attribute_list
