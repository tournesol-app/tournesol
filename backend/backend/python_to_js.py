import json


def generate_js_code(data, comments, prefix='', var_format='export const %s = '):
    """Get javascript code for constants/dictionaries."""
    assert isinstance(data, dict), f"Please provide a dict argument {data}"
    assert isinstance(comments, dict)

    result = prefix

    for var_name in data.keys():
        json_data = json.dumps(data[var_name], indent=4)
        result += f"// {comments.get(var_name, var_name)}\n"
        json_data = json_data.replace('"', '\"')
        var_set_str = var_format % var_name
        result += f"{var_set_str}JSON.parse(`{json_data}`);\n\n"

    return result.strip()
