from playerstars_domain import BasicEntity, BasicValue
from playerstars_adapters.graphql import (
    Mutation,
    MutationPrefix)

import inspect
import logging
import marshmallow


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

    '''
    def get_object_attribute_list(self, entity):
        self.logger.info('Mount entity attribute list')
        attributes = inspect.getmembers(entity,
                                        lambda a: not(inspect.isroutine(a)))
        fields_description = entity.Schema._declared_fields
        filtered_attributes = [a for a in attributes
                               if not(a[0].startswith('_'))
                               and not(a[0].endswith('_'))
                               and not(a[0].startswith('__')
                                       and a[0].endswith('__'))]
        result = dict()
        for item in filtered_attributes:
            item_type = type(item[1])
            item_name = item[0]
            item_value = item[1]

            if item_type == marshmallow.schema.SchemaMeta or \
                    isinstance(item[1], BasicGraphqlAdapter):
                continue
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

            if isinstance(item_value, BasicEntity) or isinstance(item_value,
                                                                 BasicValue):
                item_info['is_custom'] = True
                item_info['value'] = self.get_object_attribute_list(
                    item_value)
            else:
                item_info['is_custom'] = False
                item_info['value'] = item_value

            if item_value:
                result[item_name] = item_info

        return result
    '''

    def get_object_attribute_list(self, entity):
        self.logger.info('Mount entity attribute list')
        attributes = inspect.getmembers(entity,
                                        lambda a: not(inspect.isroutine(a)))
        fields_description = entity.Schema._declared_fields
        filtered_attributes = [a for a in attributes
                               if not(a[0].startswith('_'))
                               and not(a[0].endswith('_'))
                               and not(a[0].startswith('__')
                                       and a[0].endswith('__'))]
        result = dict()
        for item in filtered_attributes:
            item_type = type(item[1])
            item_name = item[0]

            if item_type == marshmallow.schema.SchemaMeta or \
                    isinstance(item[1], BasicGraphqlAdapter):
                continue

            item_info, item_value = self._process_attribute_list_item(
                item, fields_description)

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
                    return v or default
            else:
                stack.pop()
        return default

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
        return self.search(mutation_response, 'entity_id')

    def delete(self, entity_id):
        raise NotImplementedError('Not implemented yet')

    class GraphqlAdapterScanException(BaseException):
        pass
