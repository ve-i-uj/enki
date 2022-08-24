"""KBE type encoders / decoders."""

from __future__ import annotations

import abc
import collections
import collections.abc
import copy
import dataclasses
import pickle
import struct
from dataclasses import dataclass
from typing import Any, Tuple, Iterable, Optional


class PluginType(abc.ABC):
    """Abstract class for inner implemented class of the application.

    This abstract class exists to distinguish built-in types of python
    and inner defined ones in generated code.
    """


class IKBEType(abc.ABC):
    """Type of KBE client-server communication of KBEngine.

    It's a server data decoder / encoder.
    """
    __name__: str

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


@dataclass
class _VectorData(PluginType):

    def clone(self) -> _VectorData:
        return copy.deepcopy(self)


@dataclass
class Vector2Data(_VectorData):
    x: float = 0.0
    y: float = 0.0


@dataclass
class Vector3Data(_VectorData):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def clone(self) -> Vector3Data:
        return super().clone()  # type: ignore


@dataclass
class Vector4Data(_VectorData):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 0.0


class _VectorBaseType(_BaseKBEType):

    _VECTOR_TYPE = _VectorData
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

    _VECTOR_TYPE = Vector2Data
    _DIMENSIONS = ('x', 'y')


class _Vector3Type(_VectorBaseType):

    _VECTOR_TYPE = Vector3Data
    _DIMENSIONS = ('x', 'y', 'z')


class _Vector4Type(_VectorBaseType):

    _VECTOR_TYPE = Vector4Data
    _DIMENSIONS = ('x', 'y', 'z', 'w')


class PluginFixedDict(collections.abc.MutableMapping, PluginType):
    """Plugin FixedDict."""

    def __init__(self, type_name: str, initial_data: collections.OrderedDict):
        if not isinstance(initial_data, collections.OrderedDict):
            raise TypeError(f'The argument "{initial_data}" is not an instance '
                            f'of "collections.OrderedDict"')
        self._type_name = type_name
        self._data = initial_data  # the attribute contains all possible keys

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, key: str) -> Any:
        if key not in self._data:
            raise KeyError(key)
        return self._data[key]

    def __setitem__(self, key: str, item: Any) -> None:
        if key not in self._data:
            raise KeyError(f'The PluginFixedDict instance does NOT contain '
                           f'the key "{key}"')
        should_be_type = type(self._data[key])
        if not isinstance(item, should_be_type):
            raise KeyError(f'The item "{item}" has invalid type (should '
                           f'be "{should_be_type.__name__}")')
        self._data[key] = item

    def __delitem__(self, key) -> None:
        raise TypeError('You cannot delete a key from the PluginFixedDict type')

    def __iter__(self) -> Iterable:
        return iter(self._data)

    def __contains__(self, key) -> bool:
        return key in self._data

    def __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy and avoid triggering descriptors
        inst.__dict__['_data'] = self.__dict__['_data'].copy()
        return inst

    def copy(self):
        return self.__copy__()

    @classmethod
    def fromkeys(cls, iterable, value=None):
        raise TypeError('You cannot use "fromkeys" of the PluginFixedDict type. '
                        'This makes no sense.')

    def __str__(self):
        return self._data.__str__()

    def __repr__(self):
        return f"{self.__class__.__name__}(type_name='{self._type_name}', " \
               f"initial_data={self._data})"


class _FixedDictType(_BaseKBEType):
    """Represent FIXED_DICT type."""

    def __init__(self, name):
        super().__init__(name)
        self._pairs = collections.OrderedDict()  # collections.OrderedDict[str, IKBEType]

    @property
    def default(self) -> PluginFixedDict:
        return PluginFixedDict(
            type_name=self._name,
            initial_data=collections.OrderedDict(
                [(k, t.default) for k, t in self._pairs.items()])
        )

    def decode(self, data: memoryview) -> Tuple[PluginFixedDict, int]:
        result = collections.OrderedDict()
        total_offset = 0
        for key, kbe_type in self._pairs.items():
            value, shift = kbe_type.decode(data)
            data = data[shift:]
            result[key] = value
            total_offset += shift
        return PluginFixedDict(self._name, result), total_offset

    def encode(self, value: PluginFixedDict) -> bytes:
        return b''

    def build(self, name: str,
              pairs: collections.OrderedDict[str, IKBEType]
              ) -> _FixedDictType:
        """Build a new FD by the type specification."""
        inst: _FixedDictType = self.alias(name)  # type: ignore
        inst._pairs = collections.OrderedDict()
        inst._pairs.update(pairs)
        return inst


class Array(collections.abc.MutableSequence, PluginType):
    """Plugin Array."""

    def __init__(self, of: IKBEType, type_name: str,
                 initial_data: Optional[list] = None):
        self._of: IKBEType = of
        self._type_name = type_name
        initial_data = initial_data or []
        if any(not isinstance(i, of) for i in initial_data):  # type: ignore
            raise TypeError(f'The initial data has the item with invalid type '
                            f'(initial_data = {initial_data}, should be '
                            f'the list of "{self._of.__name__}" items)')
        self._data = initial_data[:]

    def __cast(self, other):
        return other._data if isinstance(other, self.__class__) else other

    def __check_item(self, item: Any) -> bool:
        if not isinstance(item, self._of):  # type: ignore
            return False
        return True

    def __lt__(self, other):
        return self._data < self.__cast(other)

    def __le__(self, other):
        return self._data <= self.__cast(other)

    def __eq__(self, other):
        return self._data == self.__cast(other)

    def __gt__(self, other):
        return self._data > self.__cast(other)

    def __ge__(self, other):
        return self._data >= self.__cast(other)

    def __contains__(self, item):
        return item in self._data

    def __len__(self):
        return len(self._data)

    def __getitem__(self, i):
        if isinstance(i, slice):
            return self.__class__(self._of, self._type_name, self._data[i])
        return self._data[i]

    def __setitem__(self, i, item):
        if not self.__check_item(item):
            raise TypeError(f'The item "{item}" has invalid type (should '
                            f'be "{self._of.__name__}")')
        self._data[i] = item

    def __delitem__(self, i):
        del self._data[i]

    def __add__(self, other):
        raise NotImplementedError

    def __radd__(self, other):
        raise NotImplementedError

    def __iadd__(self, other):
        raise NotImplementedError

    def __mul__(self, n):
        return self.__class__(self._of, self._type_name, self._data * n)

    __rmul__ = __mul__

    def __imul__(self, n):
        self._data *= n
        return self

    def __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy and avoid triggering descriptors
        inst.__dict__['_data'] = self.__dict__['_data'].copy()
        return inst

    def __iter__(self) -> Iterable:
        return iter(self._data)

    def append(self, item):
        if not self.__check_item(item):
            raise TypeError(f'The item "{item}" has invalid type (should '
                            f'be "{self._of.__name__}")')
        self._data.append(item)

    def insert(self, i, item):
        if not self.__check_item(item):
            raise TypeError(f'The item "{item}" has invalid type (should '
                            f'be "{self._of.__name__}")')
        self._data.insert(i, item)

    def pop(self, i=-1):
        return self._data.pop(i)

    def remove(self, item):
        self._data.remove(item)

    def clear(self):
        self._data.clear()

    def copy(self):
        return self.__class__(self._of, self._type_name, self._data)

    def count(self, item):
        return self._data.count(item)

    def index(self, item, *args):
        return self._data.index(item, *args)

    def reverse(self):
        self._data.reverse()

    def sort(self, *args, **kwds):
        self._data.sort(*args, **kwds)

    def extend(self, other):
        if isinstance(other, self.__class__):
            if other._of != self._of:
                raise TypeError(f'Different types of items ("{self}" and {other}')
            self._data.extend(other._data)
            return

        if isinstance(other, list):
            for item in other:
                if not self.__check_item(item):
                    raise TypeError(
                        f'The item "{item}" has invalid type (should '
                        f'be "{self._of.__name__}")')
            self._data.extend(other)
            return
        raise TypeError(f'Use list or "{self.__class__.__name__}"')

    def __str__(self):
        return f"kbetype.Array(of={self._of.__name__}, " \
               f"type_name='{self._type_name}', initial_data={self._data})"

    def __repr__(self):
        return self._data.__repr__()


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
        return UINT32.encode(len(value)) + b''.join(self._of.encode(el) for el in value)

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
class EntityComponentData(PluginType):
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


INT8: _PrimitiveKBEType = _PrimitiveKBEType('INT8', '=b', 1, 0)
UINT8: _PrimitiveKBEType = _PrimitiveKBEType('UINT8', '=B', 1, 0)
INT16: _PrimitiveKBEType = _PrimitiveKBEType('INT16', '=h', 2, 0)
UINT16: _PrimitiveKBEType = _PrimitiveKBEType('UINT16', '=H', 2, 0)
INT32: _PrimitiveKBEType = _PrimitiveKBEType('INT32', '=i', 4, 0)
UINT32: _PrimitiveKBEType = _PrimitiveKBEType('UINT32', '=I', 4, 0)
INT64: _PrimitiveKBEType = _PrimitiveKBEType('INT64', '=q', 8, 0)
UINT64: _PrimitiveKBEType = _PrimitiveKBEType('UINT64', '=Q', 8, 0)
FLOAT: _PrimitiveKBEType = _PrimitiveKBEType('FLOAT', '=f', 4, 0.0)
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
