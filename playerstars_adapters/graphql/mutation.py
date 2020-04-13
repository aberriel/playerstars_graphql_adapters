from appsyncclient import AppSyncClient
from datetime import datetime
from enum import Enum

import json
import logging


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
        self.mutation_name = mutation_name
        self.attribute_description_list = attribute_description_list
        self.api_id = api_id
        self.api_key = api_key
        self.aws_region = aws_region
        self._logger = logger if logger else logging.getLogger(__name__)

    @property
    def logger(self):
        return self._logger

    def _process_item_value_for_mutation(self, item_value):
        if isinstance(item_value, datetime):
            return item_value.strftime('%Y-%m-%dT%H:%M:%S.%f')
        elif isinstance(item_value, Enum):
            return item_value.value
        return item_value

    def mount_value_declaration_part(self, attribute_description_list):
        self.logger.debug('Mounting value declaration part of mutation query')
        response = '{\n'
        for key, value in attribute_description_list.items():
            if value['is_custom']:
                response = response + '{0}: {1}\n'\
                    .format(key,
                            self.mount_value_declaration_part(value['value']))
            else:
                response = response + '{0}: "{1}"\n'.format(
                    key,
                    self._process_item_value_for_mutation(value['value']))
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
          ''' % (self.mutation_name.capitalize(),
                 self.mutation_name,
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
