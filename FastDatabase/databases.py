import os
import threading
from queue import Queue
from typing import Callable, Any, Optional, Dict

from .encoders import DatabaseEncoder
from .exceptions import DataError


class DatabaseProperty:
    def __init__(self, name, path=None, cast=None, get_wrapper: Callable[['BaseDatabase', Any], Any] = None, set_validator: Callable[['BaseDatabase', Any], bool] = None):
        if path is None:
            path = name

        self.name = name
        self.path = path
        self.cast = cast
        self.get_wrapper = get_wrapper
        self.set_validator = set_validator

    def fget(self, database: 'BaseDatabase'):
        if self.get_wrapper:
            return self.get_wrapper(database, database.get_data(self.path, self.cast))
        else:
            return database.get_data(self.path, self.cast)

    def fset(self, database: 'BaseDatabase', value):
        if self.set_validator is None or self.set_validator(database, value):
            database.set_data(self.path, value)
        else:
            raise ValueError(f"value '{value}' is not acceptable by '{self.name}'")


class BaseDatabase:
    def __init__(self, file_path: str, encoder: DatabaseEncoder, create_if_missing: bool = True, default_data=None, encoding='utf8'):
        self._file_path = file_path
        self._encoding = encoding
        self._encoder = encoder

        self._create_if_missing = create_if_missing is True
        self._default_data = default_data if default_data is not None else {}
        self._cache = None

    def save_data(self, clean_cache=True):
        with open(file=self._file_path, mode='w', encoding=self._encoding) as file:
            file.write(self._encoder.encode(self._cache))

        if clean_cache:
            self._cache = None

    def load_data(self):
        if not os.path.exists(self._file_path):
            if self._create_if_missing:
                os.makedirs(self._file_path[:self._file_path.rfind('/')], exist_ok=True)
                self._cache = self._default_data.copy()
                self.save_data(False)
            else:
                raise FileNotFoundError(f'"{self._file_path}" does not exists')

        with open(file=self._file_path, mode='r', encoding=self._encoding) as file:
            self._cache = self._encoder.decode(file.read())

    def get_data(self, path: str = None, cast: Optional[type, Callable[[Any], Any]] = None):
        data = self._cache.copy()
        if path is None:
            return data

        pattern = path.split('.')
        for key in pattern:
            if isinstance(data, dict):
                if key in data.keys():
                    data = data[key]
                else:
                    return None
            elif isinstance(data, list):
                try:
                    data = data[int(key)]
                except Exception:
                    return None
            else:
                return None

        return data if cast is None or data is None else cast(data)

    def set_data(self, path: str, value, default: bool = False):
        data = self._cache
        pattern = path.split('.')
        for key in pattern[:-1]:
            if isinstance(data, dict):
                if key in data.keys():
                    data = data[key]
                else:
                    data[key] = {}
                    data = data[key]
            elif isinstance(data, list):
                index = int(key)
                if index == len(data):
                    data.append({})

                data = data[index]
            else:
                raise DataError('Only `dict` or `list` is accepted while navigating in data')

        if isinstance(data, dict) and (default is False or pattern[-1] not in data.keys()):
            data[pattern[-1]] = value
        elif isinstance(data, dict) and (default is False or pattern[-1] not in data.keys()):
            data[int(pattern[-1])] = value
        else:
            raise DataError('Only `dict` or `list` is accepted while navigating in data')

    def exists(self, path: str) -> bool:
        return self.get_data(path) is not None

    def remove(self, path):
        data = self.load_data()

        pattern = path.split('.')

        target = data
        for key in pattern[:-1]:
            if key in target.keys():
                target = target[key]
            else:
                return False

        if pattern[-1] not in target.keys():
            return False
        target.pop(pattern[-1])
        self.save_data(data)
        return True

    def delete(self, *, confirm: bool):
        if confirm:
            os.remove(self._file_path)

    def close(self):
        pass

    def add_property(self, name: str, path: str = None, cast=None, default=None, *, get_wrapper: Callable[['BaseDatabase', Any], Any] = None, set_validator: Callable[['BaseDatabase', Any], bool] = None):
        setattr(self, name, DatabaseProperty(name, path, cast, get_wrapper, set_validator))
        setattr(self, name, default)

    def __setattr__(self, key, value):
        try:
            v = super(BaseDatabase, self).__getattribute__(key)
            if isinstance(v, DatabaseProperty):
                v.fset(self, value)
                return
        except Exception:
            pass

        super(BaseDatabase, self).__setattr__(key, value)

    def __getattribute__(self, item):
        v = super(BaseDatabase, self).__getattribute__(item)
        if isinstance(v, DatabaseProperty):
            return v.fget(self)
        else:
            return v


class ManualDatabase(BaseDatabase):
    def get_data(self, path: str = None, cast: type = None):
        if self._cache is None:
            self.load_data()

        return super(ManualDatabase, self).get_data(path, cast)


class OnCloseDatabase(BaseDatabase):
    def __init__(self, file_path: str, encoder: DatabaseEncoder, create_if_missing: bool = True, default_data=None, encoding='utf8'):
        super().__init__(file_path, encoder, create_if_missing, default_data, encoding)

        self.load_data()

    def __del__(self):
        self.save_data()

    def save_data(self, _ignored=False):
        super(OnCloseDatabase, self).save_data(False)


class OnChangeDatabase(BaseDatabase):
    def get_data(self, path: str = None, cast: Optional[type, Callable[[Any], Any]] = None):
        self.load_data()

        value = super(OnChangeDatabase, self).get_data(path, cast)

        self._cache = None

        return value

    def set_data(self, path: str, value, default: bool = False):
        self.load_data()

        super(OnChangeDatabase, self).set_data(path, value, default)

        self.save_data()


class ThreadSafeDatabase(BaseDatabase):
    __storage: Dict[str, 'ThreadSafeDatabase'] = {}
    __thread = None

    def __new__(cls, file_path, *args, **kwargs):
        if not ThreadSafeDatabase.__thread.is_alive():
            ThreadSafeDatabase.__thread = threading.Thread(target=ThreadSafeDatabase.__worker, daemon=True)
            ThreadSafeDatabase.__thread.start()

        if file_path in ThreadSafeDatabase.__storage.keys():
            return ThreadSafeDatabase.__storage[file_path]

        ThreadSafeDatabase.__storage[file_path] = super().__new__(cls)
        return ThreadSafeDatabase.__storage[file_path]

    @staticmethod
    def __worker():
        for database in ThreadSafeDatabase.__storage.values():
            if not database._queue.empty():
                while not database._queue.empty():
                    data = database._queue.get()

                    BaseDatabase.set_data(database, data[0], data[1], data[2])

    def __init__(self, file_path: str, encoder: DatabaseEncoder, create_if_missing: bool = True, default_data=None, encoding='utf8'):
        super().__init__(file_path, encoder, create_if_missing, default_data, encoding)

        self._queue = Queue()

    def get_data(self, path: str = None, cast: Optional[type, Callable[[Any], Any]] = None):
        while not self._queue.empty():
            pass

        return super(ThreadSafeDatabase, self).get_data(path, cast)

    def set_data(self, path: str, value, default: bool = False):
        self._queue.put((path, value, default))
