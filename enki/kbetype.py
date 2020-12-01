"""KBE type mappings."""

import abc
import struct
from typing import Any


class IKBEType(abc.ABC):

    @abc.abstractproperty
    def size(self) -> int:
        pass

    @abc.abstractproperty
    def default(self) -> Any:
        pass

    @abc.abstractmethod
    def decode(self, data: bytes) -> Any:
        pass

    @abc.abstractmethod
    def encode(self, value: Any) -> bytes:
        pass


class _KBEType(IKBEType):
    
    def __init__(self, name: str, fmt: str, size: int, default: Any):
        self._name = name
        self._fmt = fmt
        self._size = size
        self._default = default

    @property
    def size(self):
        return self._size

    @property
    def default(self):
        return self._default

    def decode(self, data: bytes) -> Any:
        return struct.unpack(self._fmt, data[:self._size])[0]
    
    def encode(self, value: Any) -> bytes:
        return struct.pack(self._fmt, value)
        

class _Blob(IKBEType):
    
    def __init__(self, name: str):
        self._name = name
        self._size = 0

    @property
    def size(self):
        return self._size

    @property
    def default(self):
        return b''

    def decode(self, data: bytes):        
        lenght = INT32.decode(data)
        shift = INT32.size
        self._size = shift + lenght
        return struct.unpack(f'={lenght}ss', data[shift:self._size])[0]

    def encode(self, value) -> str:
        return struct.pack("=I%ss" % len(value), len(value), value)
    
        
class _String(IKBEType):
    
    _NULL_TERMINATOR = b'\x00'
    
    def __init__(self, name: str):
        self._name = name
        self._size = 0

    @property
    def size(self):
        return self._size

    @property
    def default(self):
        return ''

    def decode(self, data: bytes):       
        index = data.index(b'\x00') 
        self._size = index + 1  # string + null terminator
        return data[:index].decode()
    
    def encode(self, value):
        value = value.encode("utf-8")
        return struct.pack("=%ss" % (len(value) + 1), value)


class _Bool(_KBEType):

    def __init__(self, name: str):
        self._name = name

    @property
    def size(self):
        return INT8.size

    @property
    def default(self):
        return False

    def decode(self, data: bytes):
        return INT8.decode(data) > 0

    def encode(self, value):
        INT8.encode(1 if value else 0)


INT8 = _KBEType('INT8', '=b', 1, 0)
UINT8 = _KBEType('UINT8', '=B', 1, 0)
INT16 = _KBEType('INT16', '=h', 2, 0)
UINT16 = _KBEType('UINT16', '=H', 2, 0)
INT32 = _KBEType('INT32', '=i', 4, 0)
UINT32 = _KBEType('UINT32', '=I', 4, 0)
INT64 = _KBEType('INT64', '=q', 8, 0)
UINT64 = _KBEType('UINT64', '=Q', 8, 0)
FLOAT = _KBEType('FLOAT', '=f', 4, 0.0)
DOUBLE = _KBEType('DOUBLE', '=d', 8, 0.0)
BOOL = _Bool('BOOL')
BLOB = _Blob('BLOB')
STRING = _String('STRING')
