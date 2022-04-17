from .databases import BaseDatabase, OnCloseDatabase, OnChangeDatabase, ManualDatabase, ThreadSafeDatabase
from .encoders import DatabaseEncoder
from .methods import DataMethod


class Database(BaseDatabase):
    def __new__(cls, file_path: str, encoder: DatabaseEncoder, create_if_missing: bool = True, default_data=None, encoding='utf8', method: DataMethod = DataMethod.OnClose):
        if method == DataMethod.OnClose:
            return OnCloseDatabase(file_path, encoder, create_if_missing, default_data, encoding)
        if method == DataMethod.OnChange:
            return OnChangeDatabase(file_path, encoder, create_if_missing, default_data, encoding)
        if method == DataMethod.Manual:
            return ManualDatabase(file_path, encoder, create_if_missing, default_data, encoding)
        if method == DataMethod.ThreadSafe:
            return ThreadSafeDatabase(file_path, encoder, create_if_missing, default_data, encoding)

        raise TypeError(f'provided method is invalid')


class JSONDatabase(Database):
    def __init__(self, file_path: str, create_if_missing: bool = True, default_data=None, encoding='utf8', method: DataMethod = DataMethod.OnClose):
        super().__init__(file_path, DatabaseEncoder.JSON, create_if_missing, default_data, encoding, method)


class YAMLDatabase(Database):
    def __init__(self, file_path: str, create_if_missing: bool = True, default_data=None, encoding='utf8', method: DataMethod = DataMethod.OnClose):
        super().__init__(file_path, DatabaseEncoder.YAML, create_if_missing, default_data, encoding, method)
