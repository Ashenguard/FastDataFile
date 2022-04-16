from .encoders import DatabaseEncoder
from .methods import DataMethod


class Database:
    def __init__(self, file_path: str, encoder: DatabaseEncoder, create_if_missing: bool = True, default_data=None, encoding='utf8', method: DataMethod = DataMethod.OnClose):
        pass


class JSONDatabase(Database):
    def __init__(self, file_path: str, create_if_missing: bool = True, default_data=None, encoding='utf8', method: DataMethod = DataMethod.OnClose):
        super().__init__(file_path, DatabaseEncoder.JSON, create_if_missing, default_data, encoding, method)


class YAMLDatabase(Database):
    def __init__(self, file_path: str, create_if_missing: bool = True, default_data=None, encoding='utf8', method: DataMethod = DataMethod.OnClose):
        super().__init__(file_path, DatabaseEncoder.YAML, create_if_missing, default_data, encoding, method)
