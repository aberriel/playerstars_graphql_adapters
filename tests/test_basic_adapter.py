from appsyncclient import AppSyncClient
from datetime import datetime
from playerstars_graphql_adapters import (
    BasicGraphqlAdapter,
    Mutation)
from pytest import raises
from tests.basic_adapter_utils import (
    api_id,
    api_key,
    aws_region,
    ContactType,
    Person,
    person_attribute_list,
    person_creation_datetime,
    Telephone)
from unittest.mock import patch


def make_telephone_data(country_code: str = '55',
                        local_code: str = '21',
                        number: str = '99144-1522'):
    telephone = Telephone(
        country_code=country_code,
        local_code=local_code,
        number=number)
    return telephone


def make_person_data(name: str = 'Anselmo Lira',
                     contact_type: ContactType = ContactType.CLIENT,
                     comments=None):
    telephone_data = make_telephone_data()
    person_data = Person(
        entity_id='person123',
        name=name,
        telephone=telephone_data,
        contact_type=contact_type,
        comments=comments,
        creation_datetime=person_creation_datetime)
    return person_data


submit_mutation_response = {
    'data': {
        'createPerson': {
            'entity_id': 'person123',
            'name': 'Anselmo Lira',
            'contact_type': 'client',
            'creation_datetime': '2020-04-13T15:42:06.88967',
            'telephone': {
                'country_code': '55',
                'local_code': '21',
                'number': '99144-1522'
            }
        }
    }
}


submit_mutation_response_error = {
    'data': {'createPerson': None},
    'errors': [
        {
            'path': ['createPerson'],
            'data': {
                'entity_id': 'person123',
                'name': 'Anselmo Lira',
                'contact_type': 'client',
                'creation_datetime': '2020-04-13T15:42:06.88967',
                'telephone': {
                    'country_code': '55',
                    'local_code': '21',
                    'number': '99144-1522'
                }
            },
            'errorType': 'DynamoDB:ConditionalCheckFailedException',
            'errorInfo': None,
            'locations': [{'line': 3, 'column': 17, 'sourceName': None}],
            'message': 'The conditional request failed (Service: '
                       'AmazonDynamoDBv2; Status Code: 400; Error Code: '
                       'ConditionalCheckFailedException; Request ID: '
                       'MI11S9F1MAI55L2FVFV15SJHN3VV4KQNSO5AEMVJF66Q9ASUAAJG)'
        }
    ]
}


def test_basic_graphql_adapter():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    assert basic_adapter


def test_create_data_mutation():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    assert basic_adapter.create_data_mutation == 'createObject'


def test_update_data_mutation():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    assert basic_adapter.update_data_mutation == 'updateObject'


def test_delete_data_mutation():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    assert basic_adapter.delete_data_mutation == 'deleteObject'


person_birthday = datetime(1986, 12, 16)


@patch.object(AppSyncClient, 'execute', return_value=submit_mutation_response)
@patch('boto3.resource')
@patch('boto3.client')
def test_save(client, resource, app_sync_execute):
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Person')
    person_data = make_person_data()
    person_data.set_adapter(basic_adapter)

    save_result = basic_adapter.save(person_data)
    app_sync_execute.assert_called_once()
    assert save_result == 'person123'


@patch.object(AppSyncClient, 'execute',
              return_value=submit_mutation_response_error)
@patch('boto3.resource')
@patch('boto3.client')
def test_save_with_error(client, resource, app_sync_execute):
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Person')
    person_data = make_person_data()
    person_data.set_adapter(basic_adapter)

    with raises(Exception) as exc:
        basic_adapter.save(person_data)
    assert "An error of type DynamoDB:ConditionalCheckFailedException " \
           "occurred:" in str(exc.value)


def test_delete():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Person')
    with raises(NotImplementedError) as exc:
        basic_adapter.delete('obj123')
    assert 'Not implemented yet' in str(exc.value)


def test_get_attribute_list():
    person_data = make_person_data()
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Person')
    person_data.set_adapter(basic_adapter)
    attribute_list = basic_adapter.get_object_attribute_list(person_data)

    assert attribute_list
    assert isinstance(attribute_list, dict)
    assert attribute_list == person_attribute_list


def test_get_attribute_list_raise_required_field():
    telephone_data = make_telephone_data()
    person_data = Person(
        entity_id='person123',
        name=None,
        telephone=telephone_data,
        contact_type=ContactType.CLIENT,
        comments=None,
        creation_datetime=person_creation_datetime)
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Person')
    person_data.set_adapter(basic_adapter)

    with raises(Exception) as exc:
        basic_adapter.get_object_attribute_list(person_data)
    assert 'Field name is required' in str(exc.value)


def test_list_all():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Person')
    with raises(NotImplementedError) as exc:
        basic_adapter.list_all()
    assert 'Not implemented yet' in str(exc.value)


def test_get_by_id():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Person')
    with raises(NotImplementedError) as exc:
        basic_adapter.get_by_id('obj123')
    assert 'Not implemented yet' in str(exc.value)


def test_filter():
    basic_adapter = BasicGraphqlAdapter(
        api_id=api_id,
        api_key=api_key,
        aws_region=aws_region,
        object_name='Object')
    with raises(NotImplementedError) as exc:
        basic_adapter.filter()
    assert 'Not implemented yet' in str(exc.value)


def test_mount_value_declaration_part():
    mutation = Mutation(mutation_name='createPerson',
                        attribute_description_list=person_attribute_list,
                        api_id=api_id,
                        api_key=api_key,
                        aws_region=aws_region)
    value_declaration_part = mutation.mount_value_declaration_part(
        person_attribute_list)
    assert value_declaration_part
    assert isinstance(value_declaration_part, str)
    assert value_declaration_part == '''{
contact_type: "client"
creation_datetime: "2020-04-13T15:42:06.088967"
entity_id: "person123"
name: "Anselmo Lira"
address: "default address"
telephone: {
country_code: "55"
local_code: "21"
number: "99144-1522"
}
}'''


def test_mount_attribute_list_part():
    mutation = Mutation(mutation_name='createPerson',
                        attribute_description_list=person_attribute_list,
                        api_id=api_id,
                        api_key=api_key,
                        aws_region=aws_region)
    attribute_list_part = mutation.mount_attribute_list_part(
        person_attribute_list)
    assert attribute_list_part
    assert isinstance(attribute_list_part, str)
    assert attribute_list_part == '''{
contact_type
creation_datetime
entity_id
name
address
telephone{
country_code
local_code
number}}'''


def test_mount_query_mutation():
    mutation = Mutation(mutation_name='createPerson',
                        attribute_description_list=person_attribute_list,
                        api_id=api_id,
                        api_key=api_key,
                        aws_region=aws_region)
    query_mutation = mutation.mount_query_mutation()
    assert query_mutation
    assert isinstance(query_mutation, str)
    assert query_mutation == '''
               mutation Createperson {
                    createPerson (input: {
contact_type: "client"
creation_datetime: "2020-04-13T15:42:06.088967"
entity_id: "person123"
name: "Anselmo Lira"
address: "default address"
telephone: {
country_code: "55"
local_code: "21"
number: "99144-1522"
}
})
                    {
contact_type
creation_datetime
entity_id
name
address
telephone{
country_code
local_code
number}}
               }
          '''
