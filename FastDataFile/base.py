from FastDataFile import DataFileEncoder


class BaseDataFile:
    def __init__(self, file_path: str, encoder: DataFileEncoder, create_if_missing: bool = True, default_data=None, encoding='utf8'):
        self._file_path = file_path if re.match('^\.[/\\\]', file_path) else '.\\' + file_path
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

    def get_data(self, path: str = None, cast: Union[type, Callable[[Any], Any]] = None):
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