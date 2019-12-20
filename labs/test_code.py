from appsyncclient import AppSyncClient
from datetime import datetime
from enum import Enum
from marshmallow import fields, post_load, Schema
from marshmallow.validate import OneOf

import json

class MutationPrefix(Enum):
     CREATE = 'create'
     UPDATE = 'update'
     DELETE = 'delete'


class Mutation:
     def __init__(self, mutation_name, attribute_description_list):
          self.mutation_name = mutation_name
          self.attribute_description_list = attribute_description_list
     def mount_value_declaration_part(self, attribute_description_list):
          response = '{\n'
          for key, value in attribute_description_list.items():
               if value['is_custom']:
                    response = response + '{0}: {1}\n'.format(key, self.mount_value_declaration_part(value['value']))
               else:
                    response = response + '{0}: "{1}"\n'.format(key, value['value'].strftime('%Y-%m-%dT%H:%M:%S') if isinstance(value['value'], datetime) else value['value'])
          response = response + '}'
          return response
     def mount_attribute_list_part(self, attribute_description_list):
          response = '{'
          for key, value in attribute_description_list.items():
               response = response + '\n{0}'.format(key)
               if value['is_custom']:
                    response = response + mount_attribute_list_part(value['value'])
          response = response + '}'
          return response
     def mount_query_mutation(self):
          part_1 = self.mount_value_declaration_part(self.attribute_description_list)
          part_2 = self.mount_attribute_list_part(self.attribute_description_list)
          mutation_query = '''
               mutation %s {
                    %s (input: %s)
                    %s
               }
          ''' % (self.mutation_name.capitalize(), self.mutation_name, part_1, part_2)
          return mutation_query
     def submit(self):
          query = {'query': self.mount_query_mutation()}
          print(query)
          appsyncclient = AppSyncClient(apiId='3l2u7ok2cjfwdclv5qz3zb5z54', apiKey='da2-xqu7fukowrcilcwoxvcjsrfawm', region='us-east-1')
          query_json = json.dumps(query)
          response = appsyncclient.execute(data=query_json, callback=None)
          return response



class PersonAdapter:
     def __init__(self, object_name, create_mutation_name=None, update_mutation_name=None, delete_mutation_name=None, logger=None):
          self.object_name = object_name
          self.create_mutation_name = create_mutation_name or '{0}{1}'.format(MutationPrefix.CREATE.value, object_name)
          self.update_mutation_name = update_mutation_name or '{0}{1}'.format(MutationPrefix.UPDATE.value, object_name)
          self.delete_mutation_name = delete_mutation_name or '{0}{1}'.format(MutationPrefix.DELETE.value, object_name)
          self._logger = logger if logger else logging.getLogger(object_name)
     def create(self, object_to_save):
          object_attribute_description_list = object_to_save.attribute_list()
          mutation = Mutation(
               mutation_name=self.create_mutation_name,
               attribute_description_list=object_attribute_description_list)
          mutation_response = mutation.submit()
          print(mutation_response)
     def update(self, object_to_save):
          object_attribute_description_list = object_to_save.attribute_list()
          mutation_query = Mutation(
               mutation_name=self.update_mutation_name,
               attribute_description_list=object_attribute_description_list)
          mutation_response = mutation.submit()
          print(mutation_response)


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
     def __eq__(self, other):
          return self.entity_id == other.entity_id
     def to_json(self):
          return self.Schema().dump(self)
     def set_adapter(self, adapter):
          self.adapter = adapter
     def attribute_list(self):
          attributes = inspect.getmembers(self, lambda a:not(inspect.isroutine(a)))
          fields_description = self.GraphQLModelSchema._declared_fields
          filtered_attributes = [a for a in attributes if not(a[0].startswith('_')) and not(a[0].endswith('_')) and not(a[0].startswith('__') and a[0].endswith('__'))]
          result = dict()
          for item in filtered_attributes:
               item_type = type(item[1])
               if item_type == marshmallow.schema.SchemaMeta or item_type == PersonAdapter:
                    continue
               item_name = item[0]
               item_value = item[1]
               default_value = fields_description[item[0]].default
               if not item_value and (not isinstance(default_value, marshmallow.utils._Missing) and default_value is not None):
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
                    item_info['value'] = item_value.attribute_list()
               else:
                    item_info['is_custom'] = False
                    item_info['value'] = item_value
               if item_value:
                    result[item_name] = item_info
          return result
     def create(self):
          my_id = self.adapter.create(self)
          #return my_id
     def update(self):
          my_id = self.adapter.create(self)
          #return my_id
     def delete(selt):
          self.adapter.delete(self.entity_id)
     class GraphQLModelSchema(Schema):
          entity_id = fields.String(required=True, allow_none=False)


class Telephone(BasicEntity):
     def __init__(self, local_code, number, entity_id=None):
          super(Telephone, self).__init__(entity_id=entity_id)
          self.local_code = local_code
          self.number = number
     def to_string(self):
          return '({0}) {1}'.format(self.local_code, self.number)
     class GraphQLModelSchema(BasicEntity.GraphQLModelSchema):
          local_code = fields.String(required=True, allow_none=False)
          number = fields.String(required=True, allow_none=False)
          @post_load
          def post_load(self, data, many, partial):
               return Telephone(**data)


class Person(BasicEntity):
     def __init__(self, name, age=None, telephone=None, entity_id=None):
          super(Person, self).__init__(entity_id=entity_id)
          self.name = name
          self.age = age
          self.telephone = telephone
     def to_string(self):
          return '{0} - {1} ano(s)'.format(self.name, self.age)
     class GraphQLModelSchema(BasicEntity.GraphQLModelSchema):
          name = fields.String(required=True, allow_none=False)
          age = fields.Integer(required=True, allow_none=False, default=18)
          telephone = fields.Nested(Telephone.GraphQLModelSchema, required=False)
          @post_load
          def post_load(self, data, many, partial):
               return Person(**data)


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
     class GraphQLModelSchema(BasicEntity.GraphQLModelSchema):
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


telephone = Telephone(local_code='21', number='98018-3026')
person = Person(name='Anselmo', telephone=telephone)
adapter=PersonAdapter(object_name='Person')
person.set_adapter(adapter)

notification = Notification(player_id='1234', notification_complement='Olá')
adapter = PersonAdapter(object_name='Notification')
notification.set_adapter(adapter)
notification.create()