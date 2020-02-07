from playerstars_domain import BasicEntity
from playerstars_graphql_adapters.graphql import (
    Mutation,
    MutationPrefix
)

import inspect
import logging
import marshmallow


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

    def list_all(self):
        raise NotImplementedError

    def get_by_id(self):
        raise NotImplementedError

    def filter(self, **kwargs):
        raise NotImplementedError

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
        mutation_response = mutation.submit()
        return self.search(mutation_response, 'entity_id')

    def delete(self, entity_id):
        raise NotImplementedError

    class GraphqlAdapterScanException(BaseException):
        pass
