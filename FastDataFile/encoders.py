class DataFileEncoder:
    """
    Basic parent for all datafile encoders
    """

    def encode(self, data: dict) -> str:
        """
        Translate the data to be saved into a file
        :param data: Data to be translated to a string
        :return the translated data as string
        """
        raise NotImplementedError()

    def decode(self, data: str) -> dict:
        """
        Translate the string read from file to raw data
        :param data: Data to be translated to a dictionary
        :return the translated data as dictionary
        """
        raise NotImplementedError()

    JSON: 'DataFileEncoder' = None
    YAML: 'DataFileEncoder' = None


class __JSONEncoder(DataFileEncoder):
    from json import dumps as dumper, loads as loader

    def encode(self, data: dict) -> str:
        return self.dumper(data, indent=2)

    def decode(self, data: str) -> dict:
        return self.loader(data)


class __YAMLEncoder(DataFileEncoder):
    from yaml import safe_dump as dumper, safe_load as loader

    def encode(self, data: dict) -> str:
        return self.dumper(data, indent=2)

    def decode(self, data: str) -> dict:
        return self.loader(data)


DataFileEncoder.JSON = __JSONEncoder()
DataFileEncoder.YAML = __YAMLEncoder()
