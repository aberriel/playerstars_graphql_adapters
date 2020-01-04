from appsyncclient import AppSyncClient
from datetime import datetime
from enum import Enum
from playerstars_domain import BasicEntity

import inspect
import json
import logging
import marshmallow


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
                response = response + '{0}: {1}\n'\
                    .format(key,
                            self.mount_value_declaration_part(value['value']))
            else:
                response = response + '{0}: "{1}"\n'.format(key, value['value'].strftime('%Y-%m-%dT%H:%M:%S') if isinstance(value['value'], datetime) else value['value'])
        response = response + '}'
        return response

    def mount_attribute_list_part(self, attribute_description_list):
        response = '{'
        for key, value in attribute_description_list.items():
            response = response + '\n{0}'.format(key)
            if value['is_custom']:
                response = response + self.mount_attribute_list_part(value['value'])
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
        appsyncclient = AppSyncClient(apiId='3l2u7ok2cjfwdclv5qz3zb5z54',
                                      apiKey='da2-xqu7fukowrcilcwoxvcjsrfawm',
                                      region='us-east-1')
        query_json = json.dumps(query)
        response = appsyncclient.execute(data=query_json, callback=None)
        return response


class BasicAdapter:
    def __init__(self, object_name,
                 create_mutation_name=None,
                 update_mutation_name=None,
                 delete_mutation_name=None,
                 logger=None):
        """
        Adapter para persistência de um entity usando o GraphQL
        :param object_name: Nome do objeto para composição do nome das mutations e queries
        """
        self.object_name = object_name
        self.create_mutation_name = \
            create_mutation_name or \
            '{0}{1}'.format(MutationPrefix.CREATE.value, object_name)
        self.update_mutation_name = \
            update_mutation_name or \
            '{0}{1}'.format(MutationPrefix.UPDATE.value, object_name)
        self.delete_mutation_name = \
            delete_mutation_name or \
            '{0}{1}'.format(MutationPrefix.DELETE.value, object_name)
        self._logger = logger if logger else logging.getLogger(object_name)

    @property
    def logger(self):
        return self._logger

    def get_object_attribute_list(self, entity):
        attributes = inspect.getmembers(entity, lambda a:not(inspect.isroutine(a)))
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
                    isinstance(item[1], BasicAdapter):
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
                item_info['value'] = self.get_object_attribute_list(item_value)
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

    def create(self, object_to_save):
        object_attribute_description_list = self.get_object_attribute_list(object_to_save)
        mutation = Mutation(
            mutation_name=self.create_mutation_name,
            attribute_description_list=object_attribute_description_list)
        mutation_response = mutation.submit()
        return self.search(mutation_response, 'entity_id')

    def update(self, object_to_save):
        object_attribute_description_list = self.get_object_attribute_list(object_to_save)
        mutation = Mutation(
            mutation_name=self.update_mutation_name,
            attribute_description_list=object_attribute_description_list)
        mutation_response = mutation.submit()
        return self.search(mutation_response, 'entity_id')

    def delete(self, entity_id):
        raise NotImplementedError
