from appsyncclient import AppSyncClient
from enum import Enum

import boto3
import json
import logging


class MutationPrefix(Enum):
	CREATE = 'create'
	UPDATE = 'update'
	DELETE = 'delete'


class BasicGraphqlAdapter:
	def __init__(self, object_name, adapted_class, api_id, api_key, aws_region, logger=None):
		self._object_name = object_name
		self._class = adapted_class
		self._api_id = api_id
		self._api_key = api_key
		self._aws_region = aws_region
		self.api = self.get_api()
		self._logger = logger if logger else logging.getLogger(object_name)

	@property
	def logger(self):
		return self._logger

	def get_api(self):
		return AppSyncClient(apiId=self._api_id, apiKey=self._api_key, region=self._aws_region)

	def _get_mutation_name(self, mutation_type):
		return '{0}{1}'.format(mutation_type.value, self._object_name)

	@staticmethod
	def get_dict_value_str_by_type(item_value):
		if type(item_value) == int:
			return str(item_value)
		return '"{0}"'.format(str(item_value))

	@staticmethod
	def _clear_dict_empty_elements(dict_obj):
		for key, value in dict(dict_obj).items():
			if not value:
				del dict_obj[key]
		return dict_obj

	def prepare_object_data(self, obj_json):
		clear_obj_json = BasicGraphqlAdapter._clear_dict_empty_elements(obj_json)
		prepared_object = '{\n'
		for key, value in clear_obj_json.items():
			prepared_object = '{0}{1}: "{2}"\n'.format(
				prepared_object,
				key,
				BasicGraphqlAdapter.get_dict_value_str_by_type(value))
		prepared_object += '}'
		return prepared_object

	def mount_mutation_data(self):
		mutation_template = """
			mutation %s {
				%s (input: %s)
				{%s}
			}
		""" % ('a', 'b', 'c', 'd')

	def create(self):
		pass

	def update(self):
		pass
