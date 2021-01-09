"""KBE type mappings."""

import abc
import copy
import pickle
import struct
from dataclasses import dataclass
from typing import Any, Tuple, Dict


class IKBEType(abc.ABC):

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Type name"""
        pass

    @property
    @abc.abstractmethod
    def default(self) -> Any:
        """Default value of the type."""
        pass

    @abc.abstractmethod
    def decode(self, data: bytes) -> Tuple[Any, int]:
        """Decode bytes to a python type."""
        pass

    @abc.abstractmethod
    def encode(self, value: Any) -> bytes:
        """Encode a python type to bytes."""
        pass


class _KBEBaseType(IKBEType):

    def __init__(self, name: str):
        self._name = name
        self._aliases = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def default(self) -> Any:
        raise NotImplementedError

    def decode(self, data: bytes) -> Tuple[Any, int]:
        raise NotImplementedError

    def encode(self, value: Any) -> bytes:
        raise NotImplementedError

    def alias(self, alias_name: str):
        inst = copy.deepcopy(self)
        inst._name = alias_name
        self._aliases.append(inst)
        return inst

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self._name}')"


class _KBEType(_KBEBaseType):
    
    def __init__(self, name: str, fmt: str, size: int, default: Any):
        super().__init__(name)
        self._fmt = fmt
        self._size = size
        self._default = default

    @property
    def size(self) -> int:
        return self._size

    @property
    def default(self):
        return self._default

    def decode(self, data: bytes) -> Tuple[Any, int]:
        return struct.unpack(self._fmt, data[:self._size])[0], self._size
    
    def encode(self, value: Any) -> bytes:
        return struct.pack(self._fmt, value)


class _Blob(_KBEBaseType):

    @property
    def default(self):
        return b''

    def decode(self, data: bytes) -> Tuple[Any, int]:
        length, shift = UINT32.decode(data)
        if length == 0:
            return b'', 0
        size = shift + length
        return struct.unpack(f'={length}s', data[shift:size])[0], size

    def encode(self, value) -> str:
        return struct.pack("=I%ss" % len(value), len(value), value)

        
class _String(_KBEBaseType):
    
    _NULL_TERMINATOR = b'\x00'

    @property
    def default(self):
        return ''

    def decode(self, data: bytes) -> Tuple[Any, int]:
        index = data.index(b'\x00') 
        size = index + 1  # string + null terminator
        return data[:index].decode(), size
    
    def encode(self, value):
        value = value.encode("utf-8")
        return struct.pack("=%ss" % (len(value) + 1), value)


class _Bool(_KBEBaseType):

    @property
    def default(self):
        return False

    def decode(self, data: bytes) -> Tuple[Any, int]:
        return INT8.decode(data) > 0, INT8.size

    def encode(self, value):
        return INT8.encode(1 if value else 0)


class _RowData(_KBEBaseType):
    """Bytes for custom parsing."""

    @property
    def default(self):
        return []

    def decode(self, data: bytes) -> Tuple[bytes, int]:
        return data, len(data)

    def encode(self, value: bytes) -> bytes:
        return bytes


class _Python(_KBEBaseType):
    """Serialized python object."""

    @property
    def default(self):
        return object()

    def decode(self, data: bytes) -> Tuple[object, int]:
        str_obj, shift = STRING.decode(data)
        obj = pickle.loads(str_obj)
        return obj, len(data)

    def encode(self, value: object) -> bytes:
        str_obj = pickle.dumps(value)
        return STRING.encode(str_obj)


@dataclass
class _VectorData:
    pass


@dataclass
class _Vector2Data(_VectorData):
    x: float = 0.0
    y: float = 0.0


@dataclass
class _Vector3Data(_VectorData):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass
class _Vector4Data(_VectorData):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 0.0


class _VectorBase(_KBEBaseType):

    _VECTOR_TYPE = _VectorData
    _DIMENSIONS = tuple()

    @property
    def default(self) -> _VECTOR_TYPE:
        return self._VECTOR_TYPE()

    def decode(self, data: bytes) -> Tuple[_VECTOR_TYPE, int]:
        kwargs = {}
        field_type = FLOAT
        for field_name in self._DIMENSIONS:
            value, shift = field_type.decode(data)
            kwargs[field_name] = value

        return self._VECTOR_TYPE(**kwargs), data

    # TODO: [05.01.2021 14:20 burov_alexey@mail.ru]
    # Type should be public if I use this annotation
    def encode(self, value: _VECTOR_TYPE) -> bytes:
        raise


class Vector2(_VectorBase):

    _VECTOR_TYPE = _Vector2Data
    _DIMENSIONS = ('x', 'y')


class Vector3(_VectorBase):

    _VECTOR_TYPE = _Vector3Data
    _DIMENSIONS = ('x', 'y', 'z')


class Vector4(_VectorBase):

    _VECTOR_TYPE = _Vector4Data
    _DIMENSIONS = ('x', 'y', 'z', 'w')


class _FixedDict(_KBEBaseType):
    """Represent FIXED_DICT type."""

    def __init__(self, name):
        super().__init__(name)
        self._pairs = {}  # Dict[str, IKBEType]

    @property
    def default(self) -> Dict:
        return {k: t.default for k, t in self._pairs.items()}

    def decode(self, data: bytes) -> Tuple[Any, int]:
        return None, 0

    def encode(self, value: Any) -> bytes:
        return b''

    def build(self, name: str, pairs: Dict[str, IKBEType]):
        """Build a new FD by type specification."""
        inst = self.alias(name)
        inst._pairs.update(pairs)
        return inst


class _Array(_KBEBaseType):
    """Represent array type."""

    def __init__(self, name: str):
        super().__init__(name)
        self._of = None

    @property
    def default(self):
        return []

    def decode(self, data: bytes) -> Tuple[Any, int]:
        # number of bytes contained array data
        length, shift = UINT16.decode(data)
        if length == 0:
            return self.default, shift
        size = length + shift
        return [self._of.decode(b)[0] for b in data[:length]], size

    def encode(self, value):
        if len(value) == 0:
            return UINT16.encode(0)
        return UINT16.encode(len(value)) + b''.join(self._of.encode(el) for el in value)

    def build(self, name: str, of: IKBEType):
        """Build a new ARRAY by type specification."""
        inst = self.alias(name)
        inst._of = of
        return inst

    def __str__(self) -> str:
        return f'{self._name}(of={self._of})'


class _TODO(_KBEBaseType):
    pass


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
UNICODE = _String('UNICODE')

UINT8_ARRAY = _RowData('UINT8_ARRAY')

PYTHON = _Python('PYTHON')
VECTOR2 = Vector2('VECTOR2')
VECTOR3 = Vector3('VECTOR3')
VECTOR4 = Vector4('VECTOR4')
FIXED_DICT = _FixedDict('FIXED_DICT')
ARRAY = _Array('ARRAY')
ENTITYCALL = _TODO('ENTITYCALL')
KBE_DATATYPE2ID_MAX = _TODO('KBE_DATATYPE2ID_MAX')


TYPE_BY_CODE = {
    1: STRING,
    2: UINT8,    # BOOL, DATATYPE, CHAR, DETAIL_TYPE, ENTITYCALL_CALL_TYPE
    3: UINT16,   # UNSIGNED SHORT, SERVER_ERROR_CODE, ENTITY_TYPE, ENTITY_PROPERTY_UID,
                 # ENTITY_METHOD_UID, ENTITY_SCRIPT_UID, DATATYPE_UID
    4: UINT32,   # UINT, UNSIGNED INT, ARRAYSIZE, SPACE_ID, GAME_TIME, TIMER_ID
    5: UINT64,   # DBID, COMPONENT_ID
    6: INT8,     # COMPONENT_ORDER
    7: INT16,    # SHORT
    8: INT32,    # INT, ENTITY_ID, CALLBACK_ID, COMPONENT_TYPE
    9: INT64,
    10: PYTHON,  # PY_DICT, PY_TUPLE, PY_LIST
    11: BLOB,
    12: UNICODE,
    13: FLOAT,
    14: DOUBLE,
    15: VECTOR2,
    16: VECTOR3,
    17: VECTOR4,
    18: FIXED_DICT,
    19: ARRAY,
    20: ENTITYCALL,
    21: KBE_DATATYPE2ID_MAX
}

DATATYPE_UID = UINT16.alias('DATATYPE_UID')  # Id of type from types.xml
ENTITY_ID = INT32.alias('ENTITY_ID')

PY_DICT = PYTHON.alias('PY_DICT')
PY_TUPLE = PYTHON.alias('PY_TUPLE')
PY_LIST = PYTHON.alias('PY_LIST')

TYPE_BY_NAME = {t.name: t for t in TYPE_BY_CODE.values()}  # type: Dict[str, IKBEType]

SIMPLE_TYPE_BY_NAME = {t.name: t for t in TYPE_BY_CODE.values()
                       if t.name not in (FIXED_DICT.name, ARRAY.name)}  # type: Dict[str, IKBEType]
SIMPLE_TYPE_BY_NAME[PY_DICT.name] = PY_DICT
SIMPLE_TYPE_BY_NAME[PY_TUPLE.name] = PY_TUPLE
SIMPLE_TYPE_BY_NAME[PY_LIST.name] = PY_LIST
