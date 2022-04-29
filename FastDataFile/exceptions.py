class DataError(Exception):
    pass


class DataFileIsOpen(DataError):
    pass


class PathDataError(DataError):
    pass
