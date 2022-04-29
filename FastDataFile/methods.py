import re
from typing import Union, Any

from FastDataFile.exceptions import PathDataError, DataError


def validate_path(path):
    if not isinstance(path, str):
        raise PathDataError(f'Path must be a `str` not a `{type(path).__name__}`')
    if not re.match('^[A-Za-z0-9][A-Za-z0-9.]*$', path.replace('\\.', '.')):
        raise PathDataError(f'Paths can only contain alphabets, numbers, ".", "-", "_" or space, starting only with an alphabet or number')


def get_key_and_path(path):
    index = path.replace('\\.', '  ').find('.')
    if index > -1:
        key = path[:index].replace('\\.', '.')
        path = path[index + 1:]
    else:
        key = path.replace('\\.', '.')
        path = None

    return key, path


def get_data(data: Union[dict, list, tuple], path: str):
    if path is None or data is None:
        return data

    key, path = get_key_and_path(path)

    if isinstance(data, dict):
        data = data.get(key, None) or data.get(str(key), None)
    elif isinstance(data, (list, tuple)):
        try:
            data = data[int(key)]
        except ValueError:
            raise PathDataError(f'Unable to handle `{key}` to read data from the `{type(data).__name__}`')
        except IndexError:
            data = None
    else:
        raise DataError(f'DataFile can only handle dict or list, not `{type(data).__name__}`')

    return get_data(data, path)


def set_data(data: Union[dict, list], path: str, value: Any, default: bool = False):
    key, path = get_key_and_path(path)

    if path is not None:
        # There is still another step further into data
        if isinstance(data, dict):
            if key in data.keys():
                data = data.get(key)
            else:
                temp = {}
                data[key] = temp
                data = temp
        elif isinstance(data, list):
            try:
                data = data[int(key)]
            except ValueError:
                raise PathDataError(f'Unable to handle `{key}` to read data from the `{type(data).__name__}`')
            except IndexError:
                temp = {}
                data.append(temp)
                data = temp
        else:
            raise DataError(f'DataFile can only handle dict or list, not `{type(data).__name__}`')

        set_data(data, path, value, default)
    else:
        # Reached to the last section of data, Now data must be set
        if isinstance(data, dict) and (default is False or key not in data.keys()):
            data[key] = value
        elif isinstance(data, list):
            try:
                data[int(key)] = value
            except ValueError:
                raise PathDataError(f'Unable to handle `{key}` to set data to the `{type(data).__name__}`')
            except IndexError:
                data.append(value)
        else:
            raise DataError(f'DataFile can only handle dict or list, not `{type(data).__name__}`')


def remove_data(data: Union[dict, list], path: str):
    key, path = get_key_and_path(path)

    if path.replace('\\.', '  ').find('.') > -1:
        # There is still another step further into data
        if isinstance(data, dict):
            data = data.get(key, None) or data.get(str(key), None)
        elif isinstance(data, list):
            try:
                data = data[int(key)]
            except ValueError:
                raise PathDataError(f'Unable to handle `{key}` to read data from the `{type(data).__name__}`')
            except IndexError:
                data = None
        else:
            raise DataError(f'DataFile can only handle dict or list, not `{type(data).__name__}`')

        remove_data(data, path)
    else:
        # Reached to the last section of data, Now data must be set
        key, path = get_key_and_path(path)
        if isinstance(data, (dict, list)):
            data.pop(key)
        else:
            raise DataError(f'DataFile can only handle dict or list, not `{type(data).__name__}`')
