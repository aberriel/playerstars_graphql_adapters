from appsyncclient import AppSyncClient
from datetime import datetime
from enum import Enum
from marshmallow import fields, post_load, Schema
from marshmallow.validate import OneOf
from uuid import uuid4

import inspect
import json
import logging
import marshmallow


class MutationPrefix(Enum):
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'


class Mutation:
    def __init__(self, mutation_name,
                 attribute_description_list,
                 api_id,
                 api_key,
                 aws_region):
        self.mutation_name = mutation_name
        self.attribute_description_list = attribute_description_list
        self.api_id = api_id
        self.api_key = api_key
        self.aws_region = aws_region

    def mount_value_declaration_part(self, attribute_description_list):
        response = '{\n'
        for key, value in attribute_description_list.items():
            if value['is_custom']:
                response = response + '{0}: {1}\n'\
                    .format(key,
                            self.mount_value_declaration_part(value['value']))
            else:
                response = response + '{0}: "{1}"\n'.format(
                    key,
                    value['value'].strftime('%Y-%m-%dT%H:%M:%S')
                    if isinstance(value['value'], datetime)
                    else value['value'])
        response = response + '}'
        return response

    def mount_attribute_list_part(self, attribute_description_list):
        response = '{'
        for key, value in attribute_description_list.items():
            response = response + '\n{0}'.format(key)
            if value['is_custom']:
                response = response + \
                           self.mount_attribute_list_part(value['value'])
        response = response + '}'
        return response

    def mount_query_mutation(self):
        part_1 = self.mount_value_declaration_part(
            self.attribute_description_list)
        part_2 = self.mount_attribute_list_part(
            self.attribute_description_list)
        mutation_query = '''
               mutation %s {
                    %s (input: %s)
                    %s
               }
          ''' % (self.mutation_name.capitalize(),
                 self.mutation_name,
                 part_1,
                 part_2)
        return mutation_query

    def submit(self):
        query = {'query': self.mount_query_mutation()}
        appsyncclient = AppSyncClient(apiId=self.api_id,
                                      apiKey=self.api_key,
                                      region=self.aws_region)
        query_json = json.dumps(query)
        response = appsyncclient.execute(data=query_json, callback=None)
        return response


class BasicGraphqlAdapter:
    def __init__(self, api_id,
                 api_key,
                 aws_region,
                 object_name,
                 logger=None):
        self.api_id = api_id
        self.api_key = api_key
        self.aws_region = aws_region
        self.object_name = object_name
        self._logger = logger if logger else logging.getLogger(object_name)

    @property
    def logger(self):
        return self._logger

    @property
    def create_data_mutation(self):
        return '{0}{1}'.format(MutationPrefix.CREATE.value, self.object_name)

    @property
    def update_data_mutation(self):
        return '{0}{1}'.format(MutationPrefix.UPDATE.value, self.object_name)

    @property
    def delete_data_mutation(self):
        return '{0}{1}'.format(MutationPrefix.DELETE.value, self.object_name)

    def get_object_attribute_list(self, entity):
        attributes = inspect.getmembers(entity,
                                        lambda a:not(inspect.isroutine(a)))
        fields_description = entity.Schema._declared_fields
        filtered_attributes = [a for a in attributes
                               if not(a[0].startswith('_'))
                               and not(a[0].endswith('_'))
                               and not(a[0].startswith('__')
                                       and a[0].endswith('__'))]
        result = dict()
        for item in filtered_attributes:
            item_type = type(item[1])
            if item_type == marshmallow.schema.SchemaMeta or \
                    isinstance(item[1], BasicGraphqlAdapter):
                continue
            item_name = item[0]
            item_value = item[1]
            default_value = fields_description[item[0]].default

            if not item_value and \
                    (not isinstance(default_value, marshmallow.utils._Missing)
                     and default_value is not None):
                item_value = default_value
            item_info = dict()
            item_info['name'] = item_name
            item_info['type'] = item_type
            item_info['is_required'] = fields_description[item[0]].required
            item_info['allow_none'] = fields_description[item[0]].allow_none

            if fields_description[item_name].required and not item_value:
                raise Exception('Field {0} is required'.format(item[0]))
            if isinstance(item_value, BasicEntity):
                item_info['is_custom'] = True
                item_info['value'] = \
                    self.get_object_attribute_list(item_value)
            else:
                item_info['is_custom'] = False
                item_info['value'] = item_value
            if item_value:
                result[item_name] = item_info
        return result

    def search(self, d, key, default=None):
        """Return a value corresponding to the specified key in the (possibly
        nested) dictionary d. If there is no item with that key, return
        default.
        """
        stack = [iter(d.items())]
        while stack:
            for k, v in stack[-1]:
                if isinstance(v, dict):
                    stack.append(iter(v.items()))
                    break
                elif k == key:
                    return v
            else:
                stack.pop()
        return default

    def save(self, object_to_save, new_record=True):
        object_attribute_description_list = \
            self.get_object_attribute_list(object_to_save)
        print(object_attribute_description_list)
        mutation = Mutation(
            mutation_name=self.create_data_mutation if new_record else self.update_data_mutation,
            attribute_description_list=object_attribute_description_list,
            api_id=self.api_id,
            api_key=self.api_key,
            aws_region=self.aws_region)
        mutation_response = mutation.submit()
        return self.search(mutation_response, 'entity_id')

    def delete(self, entity_id):
        raise NotImplementedError


class NotificationAdapter(BasicGraphqlAdapter):
    def __init__(self, api_id,
                 api_key,
                 aws_region,
                 object_name='Notification'):
        super(NotificationAdapter, self).__init__(
            api_id=api_id,
            api_key=api_key,
            aws_region=aws_region,
            object_name=object_name)


class EnumField(fields.Field):
    def __init__(self, enum, as_string=False, *args, **kwargs):
        super(EnumField, self).__init__(*args, **kwargs)
        self.enum = enum
        self.validators.insert(0, OneOf([v.value for v in self.enum]))

    def _serialize(self, value, attr, obj, **kwargs):
        return self.enum(value).value

    def _deserialize(self, value, attr, data, **kwargs):
        return self.enum(value)

    def _validate(self, value):
        if type(value) is self.enum:
            super()._validate(value.value)


class BasicEntity:
    def __init__(self, entity_id=None):
        self.entity_id = entity_id or str(uuid4())
        self.adapter = None

    def set_adapter(self, adapter):
        self.adapter = adapter

    @classmethod
    def from_json(cls, dict_data):
        return cls.Schema().load(dict_data)

    def to_json(self):
        return self.Schema().dump(self)

    def save(self):
        my_id = self.adapter.save(self)
        return my_id

    def update(self):
        my_id = self.adapter.save(self)
        return my_id

    def delete(self):
        self.adapter.delete(self.entity_id)

    def __eq__(self, other):
        return self.entity_id == other.entity_id

    class Schema(Schema):
        entity_id = fields.String(required=True, allow_none=False)


class NotificationStatus(Enum):
    CREATED = 'CREATED'
    SENT = 'SENT'
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    DELETED = 'DELETED'


class NotificationType(Enum):
    INFORMATIVE = 'INFORMATIVE'
    CHAMPIONSHIP_INVITE_PLAYER = 'CHAMPIONSHIP_INVITE_PLAYER'
    CHAMPIONSHIP_INVITE_TEAM = 'CHAMPIONSHIP_INVITE_TEAM'
    CHAMPIONSHIP_START = 'CHAMPIONSHIP_START'
    CHAMPIONSHIP_FINISH = 'CHAMPIONSHIP_FINISH'
    CHAMPIONSHIP_CANCEL = 'CHAMPIONSHIP_CANCEL'
    TEAM_INVITE = 'TEAM_INVITE'
    DUEL_INVITE = 'DUEL_INVITE'
    DUEL_ONGOING = 'DUEL_ONGOING'


class Notification(BasicEntity):
    def __init__(self,
                 player_id: str,
                 status: NotificationStatus = NotificationStatus.CREATED,
                 creation_datetime: datetime = datetime.utcnow(),
                 notification_type: NotificationType =
                 NotificationType.INFORMATIVE,
                 entity_id: str = None,
                 duel_id: str = None,
                 team_id: str = None,
                 championship_id: str = None,
                 notification_image: str = None,
                 notification_complement: str = None):
        super(Notification, self).__init__(entity_id=entity_id)
        self.player_id = player_id
        self.duel_id = duel_id
        self.status = status
        self.team_id = team_id
        self.championship_id = championship_id
        self.creation_datetime = creation_datetime
        self.notification_type = notification_type
        self.notification_image = notification_image
        self.notification_complement = notification_complement

    class Schema(BasicEntity.Schema):
        player_id = fields.String(required=True)
        duel_id = fields.String(default=None, missing=None, allow_none=True)
        team_id = fields.String(default=None, missing=None, allow_none=True)
        championship_id = fields.String(
            required=False,
            default=None,
            missing=None,
            allow_none=True)
        status = EnumField(NotificationStatus, required=True)
        creation_datetime = fields.DateTime(
            format='iso',
            required=True,
            allow_none=False)
        notification_type = EnumField(
            NotificationType,
            required=True,
            default=NotificationType.INFORMATIVE)
        notification_image = fields.String(
            default=None,
            missing=None,
            allow_nome=True)
        notification_complement = fields.String(
            default=None,
            missing=None,
            allow_none=True)

        @post_load
        def post_load(self, data, many, partial, **kwargs):
            return Notification(**data)


notification = Notification(player_id='1317', notification_complement='Boa noite, chato!')
adapter = NotificationAdapter(
    api_id='3l2u7ok2cjfwdclv5qz3zb5z54',
    api_key='da2-xqu7fukowrcilcwoxvcjsrfawm',
    aws_region='us-east-1')
notification.set_adapter(adapter)
notification.save()
