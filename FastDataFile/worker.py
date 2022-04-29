import uuid
from queue import Queue
from threading import Thread
from typing import Optional, Union, Callable, Any

from deprecated import deprecated

from .encoders import DataFileEncoder
from .methods import validate_path, get_data, set_data, remove_data


class QueueWorker(Queue):
    def __init__(self, data_worker: 'DataWorker'):
        super().__init__()
        self._data_worker = data_worker

        self._main_thread: Optional[Thread] = Thread(target=self.watch, daemon=True)
        self._sub_thread: Optional[Thread] = None

        self._main_thread.start()

    def watch(self):
        while True:
            if self.empty():
                self._sub_thread = None
                continue

            if self._sub_thread is not None:
                self._sub_thread.join()

            self._sub_thread = Thread(target=self.handle, daemon=False)
            self._sub_thread.start()

    def handle(self):
        if self.empty():
            return

        data = self._data_worker.read()

        while not self.empty():
            call: Callable[[dict], None] = self.get()
            try:
                call(data)
            except Exception as e:
                pass

        self._data_worker.save(data)


class DataWorker:
    def __init__(self, file_path: str, encoder: DataFileEncoder, default: Optional[dict], encoding):
        self.file_path = file_path
        self._encoding = encoding
        self._encoder = encoder

        self._queue = QueueWorker(self)

        self._data_id = None
        self._data = None

        from os import path, makedirs

        if not path.exists(self.file_path):
            if default is None:
                raise FileNotFoundError(f'"{self.file_path}" does not exists')
            else:
                makedirs(self.file_path[:self.file_path.rfind('/')], exist_ok=True)
                self.save(default)

    def save(self, data: dict = None, clean_cache: bool = True):
        data = data if data is not None else {}
        with open(file=self.file_path, mode='w', encoding=self._encoding) as file:
            file.write(self._encoder.encode(data))

        if clean_cache:
            self._cache = None

    def read(self):
        with open(file=self.file_path, mode='r', encoding=self._encoding) as file:
            return self._encoder.decode(file.read())

    # Must wait for queue, controlled by an uuid
    def get_data(self, path: str = None, cast: Union[type, Callable[[Any], Any]] = None):
        data_id = uuid.uuid4()

        if path is not None:
            validate_path(path)

        def func(cache):
            while self._data_id is not None:
                pass

            self._data = get_data(cache, path)
            self._data_id = data_id

        self._queue.put(func)

        while self._data_id != data_id:
            pass

        data = self._data
        self._data_id = None
        self._data = None
        return data if cast is None or data is None else cast(data)

    def set_data(self, path: str, value, default: bool = False):
        validate_path(path)

        self._queue.put(lambda cache: set_data(cache, path, value, default))

    @deprecated(reason='Get the data and check if it is not None')
    def exists(self, path: str) -> bool:
        return self.get_data(path) is not None

    def remove(self, path):
        validate_path(path)

        self._queue.put(lambda cache: remove_data(cache, path))
