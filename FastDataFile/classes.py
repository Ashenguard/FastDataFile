from .datafiles import BaseDataFile, OnCloseDataFile, OnChangeDataFile, ManualDataFile, ThreadSafeDataFile
from .encoders import DataFileEncoder
from .methods import DataMethod


class DataFile(BaseDataFile):
    def __new__(cls, file_path: str, encoder: DataFileEncoder, create_if_missing: bool = True, default_data=None, encoding='utf8', method: DataMethod = DataMethod.OnClose):
        if method == DataMethod.OnClose:
            return OnCloseDataFile(file_path, encoder, create_if_missing, default_data, encoding)
        if method == DataMethod.OnChange:
            return OnChangeDataFile(file_path, encoder, create_if_missing, default_data, encoding)
        if method == DataMethod.Manual:
            return ManualDataFile(file_path, encoder, create_if_missing, default_data, encoding)
        if method == DataMethod.ThreadSafe:
            return ThreadSafeDataFile(file_path, encoder, create_if_missing, default_data, encoding)

        raise TypeError(f'provided method is invalid')


class JSONDataFile(DataFile):
    def __new__(cls, file_path: str, create_if_missing: bool = True, default_data=None, encoding='utf8', method: DataMethod = DataMethod.OnClose):
        return super().__new__(cls, file_path, DataFileEncoder.JSON, create_if_missing, default_data, encoding, method)


class YAMLDataFile(DataFile):
    def __new__(cls, file_path: str, create_if_missing: bool = True, default_data=None, encoding='utf8', method: DataMethod = DataMethod.OnClose):
        return super().__new__(cls, file_path, DataFileEncoder.YAML, create_if_missing, default_data, encoding, method)
