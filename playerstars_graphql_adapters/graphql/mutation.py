from appsyncclient import AppSyncClient
from datetime import datetime
from enum import Enum

import json


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
