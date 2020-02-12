from datetime import datetime
from enum import Enum
from playerstars_adapters import Mutation
from pytest import raises
from tests.basic_adapter_utils import (
    app_sync_response_notification,
    app_sync_response_test_object,
    ContactType,
    PersonAdapter,
    Person,
    test_object_data,
    test_object_data_with_id
)
from unittest.mock import patch

import pytest


def test_search_key_on_dict():
    adapter = PersonAdapter('id', 'key', 'region', 'Person')
    dict_to_search = {
        'data': {
            'createNotification': {
                'creation_datetime': '2020-02-11T21:18:52.551053',
                'entity_id': '3aeb8e00-79f6-4150-8ed1-8748968712bd',
                'notification_complement': 'Sextou',
                'notification_type': 'INFORMATIVE',
                'player_id': 'abcd',
                'status': 'CREATED'
            }
        }
    }
    search_result = adapter.search(dict_to_search, 'entity_id')
    assert search_result == '3aeb8e00-79f6-4150-8ed1-8748968712bd'


def test_not_implemented_error_list_all():
    adapter = PersonAdapter('id', 'key', 'region', 'Person')
    with pytest.raises(NotImplementedError):
        adapter.list_all()


def test_not_implemented_error_get_by_id():
    adapter = PersonAdapter('id', 'key', 'region', 'Person')
    with pytest.raises(NotImplementedError):
        adapter.get_by_id('123')


def test_not_implemented_error_delete():
    adapter = PersonAdapter('id', 'key', 'region', 'Person')
    with pytest.raises(NotImplementedError):
        adapter.delete('123')


def test_mount_object_attribute_list():
    adapter = TestAdapter('id', 'key', 'region', 'TestObject')
    entity = TestEntity(
        name='Anselmo',
        telephone='99991-1519',
        creation_datetime=datetime(2020, 2, 10, 15, 16, 17),
        contact_type=ContactType.FRIEND,
        entity_id='aqswde1')
    entity.set_adapter(adapter)
    processed_attributes = adapter.get_object_attribute_list(
        entity)
    assert processed_attributes == {
        'name': {
            'name': 'name',
            'type': str,
            'is_required': True,
            'allow_none': False,
            'is_custom': False,
            'value': 'Anselmo'
        },
        'telephone': {
            'name': 'telephone',
            'type': str,
            'is_required': False,
            'allow_none': True,
            'is_custom': False,
            'value': '99991-1519'
        },
        'entity_id': {
            'name': 'entity_id',
            'type': str,
            'is_required': True,
            'allow_none': False,
            'is_custom': False,
            'value': 'aqswde1'
        },
        'creation_datetime': {
            'name': 'creation_datetime',
            'type': datetime,
            'is_required': True,
            'allow_none': False,
            'is_custom': False,
            'value': datetime(2020, 2, 10, 15, 16, 17)
        },
        'contact_type': {
            'name': 'contact_type',
            'type': ContactType,
            'is_required': True,
            'allow_none': False,
            'is_custom': False,
            'value': ContactType.FRIEND

        }
    }


def test_mount_create_mutation_name():
    adapter = TestAdapter('id', 'key', 'region', 'Test')
    assert adapter.create_data_mutation == 'createTest'


def test_mount_update_mutation_name():
    adapter = TestAdapter('id', 'key', 'region', 'Test')
    assert adapter.update_data_mutation == 'updateTest'


def test_mount_delete_mutation_name():
    adapter = TestAdapter('id', 'key', 'region', 'Test')
    assert adapter.delete_data_mutation == 'deleteTest'


@patch('playerstars_adapters.graphql.mutation'
       '.AppSyncClient.execute',
       return_value=app_sync_response_test_object)
@patch('boto3.resource')
@patch('boto3.client')
def test_basic_adapter_save(boto_client,
                            boto_resource,
                            app_sync_execute):
    adapter = TestAdapter('id', 'key', 'region', 'TestObject')
    entity = TestEntity('Anselmo', '99991-1519')
    entity.set_adapter(adapter)
    save_result = entity.save()

    assert save_result == 'aqswde1'
