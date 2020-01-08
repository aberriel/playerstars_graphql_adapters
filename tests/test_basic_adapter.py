from playerstars_domain import (
    Notification,
    NotificationStatus,
    NotificationType
)
from playerstars_graphql_adapters import (
    BasicGraphqlAdapter,
    NotificationAdapter
)
from unittest.mock import patch, MagicMock

import datetime
#noinspection PyPackageRequirements
import pytest
from pytest import raises


api_id = '3l2u7ok2cjfwdclv5qz3zb5z54'
api_key = 'da2-xqu7fukowrcilcwoxvcjsrfawm'
aws_region = 'us-east-1'


def test_create_mutation_name_mount():
    adapter = NotificationAdapter(api_id='id',
                                  api_key='key',
                                  aws_region='region')
    assert adapter.create_data_mutation == 'CreateNotification'


def test_update_mutation_name_mount():
    adapter = NotificationAdapter(api_id='id',
                                  api_key='key',
                                  aws_region='region')
    assert adapter.update_data_mutation == 'UpdateNotification'


def test_delete_mutation_name_mount():
    adapter = NotificationAdapter(api_id='id',
                                  api_key='key',
                                  aws_region='region')
    assert adapter.delete_data_mutation == 'DeleteNotification'


notification_attribute_list_descriptor = {
    'creation_datetime': {
        'name': 'creation_datetime',
        'type': type(datetime.datetime),
        'is_required': True,
        'allow_none': False,
        'is_custom': False,
        'value': datetime.datetime(2020, 1, 6, 23, 30, 44, 600086)
    },
    'entity_id': {
        'name': 'entity_id',
        'type': type(str),
        'is_required': True,
        'allow_none': False,
        'is_custom': False,
        'value': 'c1f37c7b-253d-474d-a63e-c2e9d9eac6d9'
    },
    'notification_complement': {
        'name': 'notification_complement',
        'type': type(str),
        'is_required': False,
        'allow_none': True,
        'is_custom': False,
        'value': 'Boa noite, chato!'
    },
    'notification_type': {
        'name': 'notification_type',
        'type': type(NotificationType),
        'is_required': True,
        'allow_none': False,
        'is_custom': False,
        'value': NotificationType.INFORMATIVE
    },
    'player_id': {
        'name': 'player_id',
        'type': type(str),
        'is_required': True,
        'allow_none': False,
        'is_custom': False,
        'value': '1317'
    },
    'status': {
        'name': 'status',
        'type': type(NotificationStatus),
        'is_required': True,
        'allow_none': False,
        'is_custom': False,
        'value': NotificationStatus.CREATED
    }
}


def test_make_object_attribute_list():
    adapter = NotificationAdapter(api_id='id',
                                  api_key='key',
                                  aws_region='region')
    notification = Notification(player_id='1317',
                                notification_complement='Boa noite, chato!')
    notification.set_adapter(adapter)
    assert adapter.get_object_attribute_list(notification) == \
           notification_attribute_list_descriptor


def test_search_item_on_dict():
    pass


def test_search_item_on_dict_not_found():
    pass


def test_mount_mutation():
    pass


def test_save_record():
    pass
