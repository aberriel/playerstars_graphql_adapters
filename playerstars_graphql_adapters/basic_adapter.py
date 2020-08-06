from appsyncclient import AppSyncClient
from datetime import datetime
from enum import Enum
from playerstars_domain import BasicEntity, BasicValue

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
                 aws_region,
                 logger=None):
        self._mutation_name = mutation_name
        self.attribute_description_list = attribute_description_list
        self.api_id = api_id
        self.api_key = api_key
        self.aws_region = aws_region
        self._logger = logger if logger else logging.getLogger(__name__)

    @property
    def logger(self):
        return self._logger

    @property
    def mutation_name(self):
        return self._mutation_name

    def _process_item_value_for_mutation(self, item_value):
        if isinstance(item_value, datetime):
            return item_value.strftime('%Y-%m-%dT%H:%M:%S.%f')
        elif isinstance(item_value, Enum):
            return item_value.value
        elif isinstance(item_value, bool):
            return 'true' if item_value else 'false'
        return item_value

    def get_mutation_item_value(self, item_key, item_value):
        if item_value['type'] == bool:
            return '{0}: {1}'.format(item_key, self._process_item_value_for_mutation(item_value['value']))
        if item_value['type'] == int:
            return '{0}: {1}'.format(item_key, str(item_value['value']))
        return '{0}: "{1}"'.format(item_key, self._process_item_value_for_mutation(item_value['value']))

    def mount_value_declaration_part(self, attribute_description_list):
        self.logger.debug('Mounting value declaration part of mutation query')
        response = '{\n'
        for key, value in attribute_description_list.items():
            if value['is_custom']:
                response = response + '{0}: {1}\n' \
                    .format(key,
                            self.mount_value_declaration_part(value['value']))
            else:
                response = response + self.get_mutation_item_value(key, value) + '\n'

        response = response + '}'
        self.logger.debug('Value declaration part of query: {0}'
                          .format(response))
        return response

    def mount_attribute_list_part(self, attribute_description_list):
        self.logger.debug('Mounting attribute list part of mutation query')
        response = '{'
        for key, value in attribute_description_list.items():
            response = response + '\n{0}'.format(key)
            if value['is_custom']:
                response = response + \
                           self.mount_attribute_list_part(value['value'])
        response = response + '}'
        self.logger.debug('Attribute list part of query: {0}'.format(response))
        return response

    def mount_query_mutation(self):
        self.logger.debug('Mounting query')
        part_1 = self.mount_value_declaration_part(
            self.attribute_description_list)
        part_2 = self.mount_attribute_list_part(
            self.attribute_description_list)
        mutation_query = '''
               mutation %s {
                    %s (input: %s)
                    %s
               }
          ''' % (self._mutation_name.capitalize(),
                 self._mutation_name,
                 part_1,
                 part_2)
        self.logger.info('Mutation query: {0}'.format(mutation_query))
        return mutation_query

    def submit(self):
        query = {'query': self.mount_query_mutation()}
        appsyncclient = AppSyncClient(apiId=self.api_id,
                                      apiKey=self.api_key,
                                      region=self.aws_region)
        query_json = json.dumps(query)
        self.logger.info('Executing mutation')
        response = appsyncclient.execute(data=query_json, callback=None)
        self.logger.info('Mutation execution response: ' + str(response))
        return response


class BasicGraphqlAdapter:
    def __init__(self, api_id: str,
                 api_key: str,
                 aws_region: str,
                 object_name: str,
                 logger=None):
        self.api_id = api_id
        self.api_key = api_key
        self.aws_region = aws_region
        self.object_name = object_name
        self._logger = logger if logger else logging.getLogger(object_name)

    @property
    def logger(self):
        return self._logger

    def list_all(self):
        raise NotImplementedError('Not implemented yet')

    def get_by_id(self, item_id):
        raise NotImplementedError('Not implemented yet')

    def filter(self, **kwargs):
        raise NotImplementedError('Not implemented yet')

    @property
    def create_data_mutation(self):
        create_data_mutation_name = '{0}{1}'.format(
            MutationPrefix.CREATE.value, self.object_name)
        self.logger.info('Create mutation name: ' + create_data_mutation_name)
        return create_data_mutation_name

    @property
    def update_data_mutation(self):
        update_data_mutation_name = '{0}{1}'.format(
            MutationPrefix.UPDATE.value, self.object_name)
        self.logger.info('Update mutation name: ' + update_data_mutation_name)
        return update_data_mutation_name

    @property
    def delete_data_mutation(self):
        delete_data_mutation_name = '{0}{1}'.format(
            MutationPrefix.DELETE.value, self.object_name)
        self.logger.info('Delete mutation name: ' + delete_data_mutation_name)
        return delete_data_mutation_name

    def _process_attribute_list_item(self, item, fields_description):
        item_type = type(item[1])
        item_name = item[0]
        item_value = item[1]

        if not item_name in fields_description:
            return None, None

        default_value = fields_description[item[0]].default

        if not item_value and \
                (not isinstance(default_value, marshmallow.utils._Missing)
                 and default_value is not None):
            item_value = default_value
            item_type = type(item_value)

        item_info = dict()
        item_info['name'] = item_name
        item_info['type'] = item_type
        item_info['is_required'] = fields_description[item[0]].required
        item_info['allow_none'] = fields_description[item[0]].allow_none

        if fields_description[item_name].required and not item_value:
            raise Exception('Field {0} is required'.format(item[0]))

        if isinstance(item_value, BasicEntity) or isinstance(item_value,
                                                             BasicValue):
            item_info['is_custom'] = True
            item_info['value'] = self.get_object_attribute_list(
                item_value)
        else:
            item_info['is_custom'] = False
            item_info['value'] = item_value

        return item_info, item_value

    def get_object_attribute_list(self, entity):
        self.logger.debug('Mount entity attribute list')
        attributes = inspect.getmembers(entity,
                                        lambda a: not (inspect.isroutine(a)))
        fields_description = entity.Schema._declared_fields
        filtered_attributes = [a for a in attributes
                               if not (a[0].startswith('_'))
                               and not (a[0].endswith('_'))]
        result = dict()
        for item in filtered_attributes:
            item_name = item[0]
            item_type = type(item[1])

            if item_type == marshmallow.schema.SchemaMeta or \
                    isinstance(item[1], BasicGraphqlAdapter) or \
                    item_name == 'adapter':
                continue

            item_info, item_value = self._process_attribute_list_item(
                item, fields_description)

            if item_value:
                result[item_name] = item_info

        return result

    def save(self, object_to_save, exec_update=False):
        object_attribute_description_list = \
            self.get_object_attribute_list(object_to_save)
        mutation = Mutation(
            mutation_name=self.create_data_mutation
            if not exec_update else self.update_data_mutation,
            attribute_description_list=object_attribute_description_list,
            api_id=self.api_id,
            api_key=self.api_key,
            aws_region=self.aws_region)
        self.logger.debug('Saving object')
        mutation_response = mutation.submit()

        mutation_name = mutation.mutation_name

        try:
            mutation_response_info = mutation_response['data'][mutation_name]
        except KeyError as e:
            msg = f'Mutation Response have no "{e}" key: ' \
                  f'"{mutation_response}"'
            raise Exception(msg)
        except TypeError as e:
            msg = f'Mutation Response have no "data" key: ' \
                  f'"{mutation_response}"'
            raise Exception(msg)

        if not mutation_response_info:
            error_info = mutation_response['errors'][0]
            raise Exception("An error of type {0} occurred: {1}"
                            .format(error_info['errorType'],
                                    error_info['message']))

        return mutation_response_info['entity_id']

    def delete(self, entity_id):
        raise NotImplementedError('Not implemented yet')

    class GraphqlAdapterScanException(BaseException):
        pass
