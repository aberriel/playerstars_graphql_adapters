from .basic_adapter_utils import (
    ContactType,
    Person,
    PersonAdapter,
    Telephone)
from datetime import datetime
from playerstars_adapters import (
    BasicGraphqlAdapter)
from pytest import raises


def make_telephone_data(country_code: str = '55',
                        local_code: str = '21',
                        number: str = '99144-1522'):
    telephone = Telephone(
        country_code=country_code,
        local_code=local_code,
        number=number)
    return telephone


def make_person_data(name: str = 'Anselmo Lira',
                     contact_type: ContactType = ContactType.CLIENT,
                     comments=None):
    telephone_data = make_telephone_data()
    person_data = Person(
        entity_id='person123',
        name=name,
        telephone=telephone_data,
        contact_type=contact_type,
        comments=comments)
    return person_data


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
        'value': datetime(2020, 4, 13, 15, 42, 6, 88967)
    },
    'entity_id': {
        'name': 'entity_id',
        'type': str,
        'is_required': True,
        'allow_none': False,
        'is_custom': False,
        'value': '2b10ff93-be29-47b1-9849-62e174ffdb00'
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


def test_basic_graphql_adapter():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    assert basic_adapter


def test_create_data_mutation():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    create_mutation_name = basic_adapter.create_data_mutation()
    assert create_mutation_name == 'createObject'


def test_update_data_mutation():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    update_mutation_name = basic_adapter.update_data_mutation()
    assert update_mutation_name == 'deleteObject'


def test_delete_data_mutation():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    delete_mutation_name = basic_adapter.delete_data_mutation()
    assert delete_mutation_name == 'deleteObject'


def test_search():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    person_json = make_person_data().to_json()
    search_result = basic_adapter.search(person_json, 'entity_id')
    assert search_result
    assert search_result == 'person123'


def test_search_none_attribute_with_default():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    person_json = make_person_data().to_json()
    search_result = basic_adapter.search(person_json, 'comments', 'default comment')
    assert search_result
    assert search_result == 'default comment'


def test_search_none_attribute_without_default():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    person_json = make_person_data().to_json()
    search_result = basic_adapter.search(person_json, 'comments')
    assert not search_result


person_birthday = datetime(1986, 12, 16)


def test_search_unknow_attribute_with_default():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    person_json = make_person_data().to_json()
    search_result = basic_adapter.search(person_json, 'birthday', person_birthday)
    assert search_result
    assert search_result == person_birthday


def test_search_unknow_attribute_without_default():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    person_json = make_person_data().to_json()
    search_result = basic_adapter.search(person_json, 'birthday')
    assert not search_result


'''
def test_save():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    person_data = make_person_data()
    person_data.set_adapter(basic_adapter)

    save_result = basic_adapter.save(person_data)
'''


def test_delete():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    with raises(NotImplementedError) as exc:
        basic_adapter.delete('obj123')
    assert 'Not implemented yet' in str(exc.value)


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
