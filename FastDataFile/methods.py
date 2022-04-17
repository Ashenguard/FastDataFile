class DataMethod:
    def __init__(self, *, _value):
        self._value = _value

    def __eq__(self, other):
        return isinstance(other, DataMethod) and self._value == self._value

    OnChange: 'DataMethod' = None
    OnClose: 'DataMethod' = None
    Manual: 'DataMethod' = None
    ThreadSafe: 'DataMethod' = None


DataMethod.OnChange = DataMethod(_value=0)
DataMethod.OnClose = DataMethod(_value=1)
DataMethod.Manual = DataMethod(_value=2)
DataMethod.ThreadSafe = DataMethod(_value=3)
