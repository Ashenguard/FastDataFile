import os
import re
from typing import Callable, Any, Union

from deprecated import deprecated

from .encoders import DataFileEncoder
from .exceptions import DataFileIsOpen
from .worker import DataWorker


class DataFileProperty:
    def __init__(self, name, path=None, cast=None, get_wrapper: Callable[['DataFile', Any], Any] = None, set_validator: Callable[['DataFile', Any], bool] = None):
        if path is None:
            path = name

        self.name = name
        self.path = path
        self.cast = cast
        self.get_wrapper = get_wrapper
        self.set_validator = set_validator

    def fget(self, datafile: 'DataFile'):
        if self.get_wrapper:
            return self.get_wrapper(datafile, datafile.get_data(self.path, self.cast))
        else:
            return datafile.get_data(self.path, self.cast)

    def fset(self, datafile: 'DataFile', value):
        if self.set_validator is None or self.set_validator(datafile, value):
            datafile.set_data(self.path, value)
        else:
            raise ValueError(f"value '{value}' is not acceptable by '{self.name}'")


class DataFile:
    __storage = {}

    def __init__(self, file_path: str, encoder: DataFileEncoder, create_if_missing: bool = True, default_data=None, encoding='utf8'):
        if file_path in DataFile.__storage.keys():
            raise DataFileIsOpen(f'Datafile `{file_path}` is currently open somewhere else. Make sure you close it or use Datafile#open instead.')

        file_path = file_path if re.match('^\.[/\\\]', file_path) else '.\\' + file_path
        file_path = file_path.replace('\\', '/')
        default_data = None if create_if_missing is not True else default_data if default_data is not None else {}

        DataFile.__storage[file_path] = self

        self._worker = DataWorker(file_path, encoder, default_data, encoding)

    @staticmethod
    def open(file_path: str, encoder: DataFileEncoder, create_if_missing: bool = True, default_data=None, encoding='utf8'):
        file_path = file_path if re.match('^\.[/\\\]', file_path) else '.\\' + file_path
        file_path = file_path.replace('\\', '/')

        return DataFile(file_path, encoder, create_if_missing, default_data, encoding) if file_path not in DataFile.__storage.keys() else DataFile.__storage[file_path]

    def get_data(self, path: str = None, cast: Union[type, Callable[[Any], Any]] = None):
        return self._worker.get_data(path, cast)

    def set_data(self, path: str, value, default: bool = False):
        self._worker.set_data(path, value, default)

    @deprecated(reason='Get the data and check if it is not None')
    def exists(self, path: str) -> bool:
        return self.get_data(path) is not None

    def remove(self, path):
        self._worker.remove(path)

    def delete(self, *, confirm: bool):
        if confirm:
            self.close(False)

            os.remove(self._file_path)

    def close(self, save: bool = True):
        if save:
            self._worker.save()

        DataFile.__storage.pop(self._worker.file_path)

    def add_property(self, name: str, path: str = None, cast=None, default=None, *, get_wrapper: Callable[['DataFile', Any], Any] = None, set_validator: Callable[['DataFile', Any], bool] = None):
        setattr(self, name, DataFileProperty(name, path, cast, get_wrapper, set_validator))
        self.set_data(path, default, True)

    def __setattr__(self, key, value):
        try:
            v = super(DataFile, self).__getattribute__(key)
            if isinstance(v, DataFileProperty):
                v.fset(self, value)
                return
        except Exception:
            pass

        super(DataFile, self).__setattr__(key, value)

    def __getattribute__(self, item):
        v = super(DataFile, self).__getattribute__(item)
        if isinstance(v, DataFileProperty):
            return v.fget(self)
        else:
            return v


class JSONDataFile(DataFile):
    def __init__(self, file_path: str, create_if_missing: bool = True, default_data=None, encoding='utf8'):
        super(JSONDataFile, self).__init__(file_path, DataFileEncoder.JSON, create_if_missing, default_data, encoding)

    # noinspection PyMethodOverriding
    @staticmethod
    def open(file_path: str, create_if_missing: bool = True, default_data=None, encoding='utf8'):
        return DataFile.open(file_path, DataFileEncoder.JSON, create_if_missing, default_data, encoding)


class YAMLDataFile(DataFile):
    def __init__(self, file_path: str, create_if_missing: bool = True, default_data=None, encoding='utf8'):
        super(YAMLDataFile, self).__init__(file_path, DataFileEncoder.YAML, create_if_missing, default_data, encoding)

    # noinspection PyMethodOverriding
    @staticmethod
    def open(file_path: str, create_if_missing: bool = True, default_data=None, encoding='utf8'):
        return DataFile.open(file_path, DataFileEncoder.YAML, create_if_missing, default_data, encoding)
