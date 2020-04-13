from playerstars_graphql_adapters.graphql.mutation import Mutation
from tests.basic_adapter_utils import (
    api_id,
    api_key,
    aws_region,
    person_attribute_list)


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
