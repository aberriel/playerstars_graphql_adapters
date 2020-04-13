from appsyncclient import AppSyncClient
from playerstars_adapters import (
    BasicGraphqlAdapter)
from pytest import raises
from tests.basic_adapter_utils import (
    ContactType,
    Person,
    Telephone)
from datetime import datetime
from unittest.mock import patch


person_creation_datetime = datetime(2020, 4, 13, 15, 42, 6, 88967)


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
        comments=comments,
        creation_datetime=person_creation_datetime)
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


submit_mutation_response = {
    'data': {
        'create_person': {
            'entity_id': 'person123',
            'name': 'Anselmo Lira',
            'contact_type': 'client',
            'creation_datetime': '2020-04-13T15:42:06.88967',
            'telephone': {
                'country_code': '55',
                'local_code': '21',
                'number': '99144-1522'
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
    assert basic_adapter.create_data_mutation == 'createObject'


def test_update_data_mutation():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    assert basic_adapter.update_data_mutation == 'updateObject'


def test_delete_data_mutation():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    assert basic_adapter.delete_data_mutation == 'deleteObject'


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
    search_result = basic_adapter.search(person_json, 'comments',
                                         'default comment')
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
    search_result = basic_adapter.search(person_json,
                                         'birthday', person_birthday)
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


@patch.object(AppSyncClient, 'execute', return_value=submit_mutation_response)
@patch('boto3.resource')
@patch('boto3.client')
def test_save(boto_client,
              boto_resource,
              app_sync_execute):
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    person_data = make_person_data()
    person_data.set_adapter(basic_adapter)

    save_result = basic_adapter.save(person_data)
    app_sync_execute.assert_called_once()
    assert save_result == 'person123'


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
    print('\ntest_get_attribute_list -> Entrando')
    person_data = make_person_data()
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    person_data.set_adapter(basic_adapter)
    attribute_list = basic_adapter.get_object_attribute_list(person_data)

    assert attribute_list
    assert isinstance(attribute_list, dict)
    assert attribute_list == person_attribute_list


def test_get_attribute_list_raise_required_field():
    telephone_data = make_telephone_data()
    person_data = Person(
        entity_id='person123',
        name=None,
        telephone=telephone_data,
        contact_type=ContactType.CLIENT,
        comments=None,
        creation_datetime=person_creation_datetime)
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    person_data.set_adapter(basic_adapter)

    with raises(Exception) as exc:
        basic_adapter.get_object_attribute_list(person_data)
    assert 'Field name is required' in str(exc.value)


def test_list_all():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    with raises(NotImplementedError) as exc:
        basic_adapter.list_all()
    assert 'Not implemented yet' in str(exc.value)


def test_get_by_id():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    with raises(NotImplementedError) as exc:
        basic_adapter.get_by_id('obj123')
    assert 'Not implemented yet' in str(exc.value)


def test_filter():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    with raises(NotImplementedError) as exc:
        basic_adapter.filter()
    assert 'Not implemented yet' in str(exc.value)
