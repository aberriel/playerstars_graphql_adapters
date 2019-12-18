def mount_object_mutation_data(object_dict):
    result = "{\n"
    for key, value in object_dict.items():
        result = '{0}: "{1}"\n'.format(key, value)
    result = result + '}'
    return result

def mount_object_attribute_list(object_dict):
    keys_list = list(object_dict.keys())
    return '{%s}' % ('\n'.join([str(elem) for elem in keys_list]))
