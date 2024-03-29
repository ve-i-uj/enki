"""KBE type serializers / deserializers."""

from __future__ import annotations

import abc
import collections
import collections.abc
import copy
import dataclasses
import pickle
import struct
from dataclasses import dataclass
from typing import Any, Generator, Tuple, Iterable, Optional, Type
from collections import OrderedDict

from enki.core.enkitype import EnkiType

from .plugintype import Vector2, Vector3, Vector4
from .plugintype import FixedDict, Array


class IKBEType(abc.ABC):
    """Type of KBE client-server communication of KBEngine.

    It's a server data decoder / encoder.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Type name"""
        pass

    @property
    @abc.abstractmethod
    def default(self) -> Any:
        """Default value of the python type."""
        pass

    @abc.abstractmethod
    def decode(self, data: memoryview) -> Tuple[Any, int]:
        """Decode bytes to a python type.

        Returns decoded data and offset.
        """
        pass

    @abc.abstractmethod
    def encode(self, value: Any) -> bytes:
        """Encode a python type to bytes."""
        pass

    @abc.abstractmethod
    def alias(self, alias_name: str) -> IKBEType:
        """Create alias of the "self" type."""
        pass


class _BaseKBEType(IKBEType):
    """Родительский класс для сериализаторов простых типов KBE (INT32, BLOB и т.д.)"""

    def __init__(self, name: str):
        self._name = name
        self._aliases = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def default(self) -> Any:
        raise NotImplementedError

    def decode(self, data: memoryview) -> Tuple[Any, int]:
        raise NotImplementedError

    def encode(self, value: Any) -> bytes:
        raise NotImplementedError

    def alias(self, alias_name: str) -> IKBEType:
        # We don't know how many attributes instance have. And it doesn't matter
        # because only type name should be changed.
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        inst._name = alias_name
        self._aliases.append(inst)
        return inst

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self._name}')"


class _PrimitiveKBEType(_BaseKBEType):
    """Easy decoding type.

    It needs only format and size. No calculation to decode / encode needed.
    """

    def __init__(self, name: str, fmt: str, size: int, default: Any):
        super().__init__(name)
        self._fmt = fmt
        self._size = size
        self._default = default

    @property
    def size(self) -> int:
        return self._size

    @property
    def default(self) -> Any:
        return self._default

    def decode(self, data: memoryview) -> Tuple[Any, int]:
        return struct.unpack(self._fmt, data[:self._size])[0], self._size

    def encode(self, value: Any) -> bytes:
        return struct.pack(self._fmt, value)


class _BlobType(_BaseKBEType):
    """Binary data."""

    @property
    def default(self):
        return b''

    def decode(self, data: memoryview) -> Tuple[bytes, int]:
        length, shift = UINT32.decode(data)
        if length == 0:
            return b'', shift
        size = shift + length
        return struct.unpack(f'={length}s', data[shift:size])[0], size

    def encode(self, value: bytes) -> bytes:
        return struct.pack("=I%ss" % len(value), len(value), value)


class _EndlessBlobType(_BaseKBEType):
    """Blob until data ends."""

    @property
    def default(self):
        return b''

    def decode(self, data: memoryview) -> Tuple[bytes, int]:
        length = len(data)
        if length == 0:
            return b'', 0
        return struct.unpack(f'={length}s', data)[0], length

    def encode(self, value: bytes) -> bytes:
        return struct.pack('=%s' % len(value), value)


class _UnicodeType(_BaseKBEType):
    """Unicode data."""

    @property
    def default(self):
        return ''

    def decode(self, data: memoryview) -> Tuple[str, int]:
        encoded, shift = BLOB.decode(data)
        return encoded.decode('utf-8'), shift

    def encode(self, value) -> bytes:
        return BLOB.encode(value.encode())


class _StringType(_BaseKBEType):
    """String data."""

    _NULL_TERMINATOR = int.from_bytes(b'\x00', 'big')

    @property
    def default(self) -> str:
        return ''

    def decode(self, data: memoryview) -> Tuple[str, int]:
        index = 0
        for index, b in enumerate(data):
            if b == self._NULL_TERMINATOR:
                break
        size = index + 1  # string + null terminator
        return data[:index].tobytes().decode(), size

    def encode(self, value: str):
        encoded = value.encode("utf-8")
        return struct.pack("=%ss" % (len(encoded) + 1), encoded)


class _BoolType(_BaseKBEType):

    @property
    def default(self) -> bool:
        return False

    def decode(self, data: memoryview) -> Tuple[bool, int]:
        return INT8.decode(data)[0] > 0, INT8.size

    def encode(self, value: bool):
        return INT8.encode(1 if value else 0)


class _RowDataType(_BaseKBEType):
    """Bytes for custom parsing."""

    @property
    def default(self) -> bytes:
        return b''

    def decode(self, data: memoryview) -> Tuple[memoryview, int]:
        return data, len(data)

    def encode(self, value: bytes) -> bytes:
        return value


class _PythonType(_BaseKBEType):
    """Pickle serialized python object."""

    @property
    def default(self) -> object:
        return object()

    def decode(self, data: memoryview) -> Tuple[object, int]:
        bytes_, shift = BLOB.decode(data)
        obj = pickle.loads(bytes_)
        return obj, shift

    def encode(self, value: object) -> bytes:
        bytes_ = pickle.dumps(value)
        return BLOB.encode(bytes_)


class _PluginVector(EnkiType):

    def clone(self) -> _PluginVector:
        return copy.deepcopy(self)


class _VectorBaseType(_BaseKBEType):

    _VECTOR_TYPE = _PluginVector
    _DIMENSIONS = tuple()

    @property
    def default(self) -> _VECTOR_TYPE:
        return self._VECTOR_TYPE()

    def decode(self, data: memoryview) -> Tuple[_VECTOR_TYPE, int]:
        kwargs = {}
        field_type = FLOAT
        offset = 0
        for field_name in self._DIMENSIONS:
            value, shift = field_type.decode(data)
            data = data[shift:]
            offset += shift
            kwargs[field_name] = value

        return self._VECTOR_TYPE(**kwargs), offset

    def encode(self, value: _VECTOR_TYPE) -> bytes:
        raise NotImplementedError


class _Vector2Type(_VectorBaseType):

    _VECTOR_TYPE = Vector2
    _DIMENSIONS = ('x', 'y')


class _Vector3Type(_VectorBaseType):

    _VECTOR_TYPE = Vector3
    _DIMENSIONS = ('x', 'y', 'z')


class _Vector4Type(_VectorBaseType):

    _VECTOR_TYPE = Vector4
    _DIMENSIONS = ('x', 'y', 'z', 'w')


class _FixedDictType(_BaseKBEType):
    """Represent FIXED_DICT type."""

    def __init__(self, name):
        super().__init__(name)
        self._pairs: OrderedDict[str, IKBEType] = OrderedDict()

    @property
    def default(self) -> FixedDict:
        return FixedDict(
            type_name=self._name,
            initial_data=OrderedDict(
                [(k, t.default) for k, t in self._pairs.items()])
        )

    def decode(self, data: memoryview) -> Tuple[FixedDict, int]:
        result = OrderedDict()
        total_offset = 0
        for key, kbe_type in self._pairs.items():
            value, shift = kbe_type.decode(data)
            data = data[shift:]
            result[key] = value
            total_offset += shift
        return FixedDict(self._name, result), total_offset

    def encode(self, value: FixedDict) -> bytes:
        data = b''
        for k, v in value.values():
            assert k in self._pairs
            data += self._pairs[k].encode(v)

        return data

    def build(self, name: str,
              pairs: OrderedDict[str, IKBEType]
              ) -> _FixedDictType:
        """Build a new FD by the type specification."""
        inst: _FixedDictType = self.alias(name)  # type: ignore
        inst._pairs = OrderedDict()
        inst._pairs.update(pairs)
        return inst


class _ArrayType(_BaseKBEType):
    """Represent array type."""

    def __init__(self, name: str):
        super().__init__(name)
        # The attribute will be set in the "build" method.
        self._of: IKBEType = None  # type: ignore

    @property
    def default(self) -> Array:
        return Array(of=type(self._of.default), type_name=self._name)

    def decode(self, data: memoryview) -> Tuple[Array, int]:
        # number of bytes contained array data
        length, shift = UINT32.decode(data)
        data = data[shift:]
        if length == 0:
            return self.default, shift
        result = []
        offset = shift
        for _ in range(length):
            value, shift = self._of.decode(data)
            data = data[shift:]
            offset += shift
            result.append(value)

        return Array(of=type(self._of.default), type_name=self._name,
                     initial_data=result), offset

    def encode(self, value: Array) -> bytes:
        if len(value) == 0:
            return UINT32.encode(0)
        return UINT32.encode(len(value)) + b''.join(self._of.encode(el) for el in value)  # type: ignore

    def build(self, name: str, of: IKBEType) -> _ArrayType:
        """Build a new ARRAY by type specification."""
        inst: _ArrayType = self.alias(name)  # type: ignore
        inst._of = of
        return inst

    def __str__(self) -> str:
        return f"{self._name}(of='{self._of}')"


class _TODOType(_BaseKBEType):
    pass


@dataclass
class EntityComponentData(EnkiType):
    component_type: int
    owner_id: int
    component_ent_id: int
    count: int
    entity_component_property_id: Optional[int] = None
    name: Optional[str] = None
    properties: dict = dataclasses.field(default_factory=dict)


class _EntityComponent(_BaseKBEType):

    @property
    def default(self) -> EntityComponentData:
        return EntityComponentData(0, 0, 0, 0)

    def decode(self, data: memoryview) -> Tuple[EntityComponentData, int]:
        shift = 0
        component_type, offset = UINT32.decode(data)
        shift += offset
        # TODO: [2022-08-27 10:31 burov_alexey@mail.ru]:
        # Тут падает. Может быть из-за того, что если прокси создана
        owner_id, offset = INT32.decode(data[shift:])
        shift += offset

        # UInt16 ComponentDescrsType ???
        component_ent_id, offset = UINT16.decode(data[shift:])
        shift += offset

        count, offset = UINT16.decode(data[shift:])
        shift += offset

        inst = EntityComponentData(
            component_type, owner_id, component_ent_id, count
        )
        return inst, shift

    def encode(self, value: Any) -> bytes:
        raise NotImplementedError


class _FloatType(_PrimitiveKBEType):

    def encode(self, value: float) -> bytes:
        # TODO: [2022-11-18 15:54 burov_alexey@mail.ru]:
        # Сервер может прислать потенциально число, которое больше,
        # чем Python может поменять по формату "f". Пока так.
        if value > 2147483647 or value < -2147483647:
            value = 0
        return super().encode(value)


INT8: _PrimitiveKBEType = _PrimitiveKBEType('INT8', '=b', 1, 0)
UINT8: _PrimitiveKBEType = _PrimitiveKBEType('UINT8', '=B', 1, 0)
INT16: _PrimitiveKBEType = _PrimitiveKBEType('INT16', '=h', 2, 0)
UINT16: _PrimitiveKBEType = _PrimitiveKBEType('UINT16', '=H', 2, 0)
INT32: _PrimitiveKBEType = _PrimitiveKBEType('INT32', '=i', 4, 0)
UINT32: _PrimitiveKBEType = _PrimitiveKBEType('UINT32', '=I', 4, 0)
INT64: _PrimitiveKBEType = _PrimitiveKBEType('INT64', '=q', 8, 0)
UINT64: _PrimitiveKBEType = _PrimitiveKBEType('UINT64', '=Q', 8, 0)
FLOAT: _PrimitiveKBEType = _FloatType('FLOAT', '=f', 4, 0.0)
DOUBLE: _PrimitiveKBEType = _PrimitiveKBEType('DOUBLE', '=d', 8, 0.0)
BOOL: _BoolType = _BoolType('BOOL')
BLOB: _BlobType = _BlobType('BLOB')
STRING: _StringType = _StringType('STRING')
UNICODE: _UnicodeType = _UnicodeType('UNICODE')

UINT8_ARRAY: _RowDataType = _RowDataType('UINT8_ARRAY')

PYTHON: _PythonType = _PythonType('PYTHON')
VECTOR2: _Vector2Type = _Vector2Type('VECTOR2')
VECTOR3: _Vector3Type = _Vector3Type('VECTOR3')
VECTOR4: _Vector4Type = _Vector4Type('VECTOR4')
FIXED_DICT: _FixedDictType = _FixedDictType('FIXED_DICT')
ARRAY: _ArrayType = _ArrayType('ARRAY')
ENTITYCALL: _TODOType = _TODOType('ENTITYCALL')
KBE_DATATYPE2ID_MAX: _TODOType = _TODOType('KBE_DATATYPE2ID_MAX')
ENTITY_COMPONENT: _EntityComponent = _EntityComponent('ENTITY_COMPONENT')

# Each type has the fixed unique id in KBEngine.
TYPE_BY_CODE: dict[int, IKBEType] = {
    1: STRING,
    2: UINT8,    # BOOL, DATATYPE, CHAR, DETAIL_TYPE, ENTITYCALL_CALL_TYPE
    3: UINT16,   # UNSIGNED SHORT, SERVER_ERROR_CODE, ENTITY_TYPE, ENTITY_PROPERTY_UID,
                 # ENTITY_METHOD_UID, ENTITY_SCRIPT_UID, DATATYPE_UID
    4: UINT32,   # UINT, UNSIGNED INT, ARRAYSIZE, SPACE_ID, GAME_TIME, TIMER_ID
    5: UINT64,   # DBID, COMPONENT_ID
    6: INT8,
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
    21: KBE_DATATYPE2ID_MAX,

    999: ENTITY_COMPONENT,
}

DATATYPE_UID = UINT16.alias('DATATYPE_UID')  # Id of type from types.xml
ENTITY_ID = INT32.alias('ENTITY_ID')

PY_DICT = PYTHON.alias('PY_DICT')
PY_TUPLE = PYTHON.alias('PY_TUPLE')
PY_LIST = PYTHON.alias('PY_LIST')

TYPE_BY_NAME = {t.name: t for t in TYPE_BY_CODE.values()}

SIMPLE_TYPE_BY_NAME = {t.name: t for t in TYPE_BY_CODE.values()
                       if t.name not in (FIXED_DICT.name, ARRAY.name)}
SIMPLE_TYPE_BY_NAME[PY_DICT.name] = PY_DICT
SIMPLE_TYPE_BY_NAME[PY_TUPLE.name] = PY_TUPLE
SIMPLE_TYPE_BY_NAME[PY_LIST.name] = PY_LIST

# *** Application defined types ***

SPACE_ID = UINT32.alias('SPACE_ID')
SERVER_ERROR = UINT16.alias('SERVER_ERROR')  # see kbeenum.ServerError
ENTITY_PROPERTY_UID = UINT16.alias('ENTITY_PROPERTY_UID')
ENTITY_METHOD_UID = UINT16.alias('ENTITY_METHOD_UID')

MESSAGE_ID = UINT16.alias('MESSAGE_ID')
MESSAGE_LENGTH = UINT16.alias('MESSAGE_LENGTH')

COMPONENT_TYPE = INT32.alias('COMPONENT_TYPE')
COMPONENT_ID: IKBEType = UINT64.alias('COMPONENT_ID')
COMPONENT_ORDER: IKBEType = INT32.alias('COMPONENT_ORDER')
COMPONENT_GUS: IKBEType = INT32.alias('COMPONENT_GUS')

ENDLESS_BLOB = _EndlessBlobType('ENDLESS_BLOB')

SHUTDOWN_STATE = INT8.alias('SHUTDOWN_STATE')

GAME_TIME = UINT32.alias('GAME_TIME')

CALLBACK_ID = UINT32.alias('CALLBACK_ID')

ENTITY_SCRIPT_UID = UINT16.alias('ENTITY_SCRIPT_UID')
DBID = UINT64.alias('DBID')
