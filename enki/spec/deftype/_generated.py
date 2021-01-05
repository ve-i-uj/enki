"""Generated types represent types of the file types.xml"""

from enki import kbetype
from . import _deftype


_UINT8_SPEC = _deftype.DataTypeSpec(
    id=1,
    base_type_name='UINT8',
    name='UINT8',    
)
UINT8 = kbetype.UINT8

_UINT16_SPEC = _deftype.DataTypeSpec(
    id=2,
    base_type_name='UINT16',
    name='UINT16',    
)
UINT16 = kbetype.UINT16

_DBID_SPEC = _deftype.DataTypeSpec(
    id=3,
    base_type_name='UINT64',
    name='DBID',    
)
DBID = kbetype.UINT64.alias('DBID')

_UINT32_SPEC = _deftype.DataTypeSpec(
    id=4,
    base_type_name='UINT32',
    name='UINT32',    
)
UINT32 = kbetype.UINT32

_INT8_SPEC = _deftype.DataTypeSpec(
    id=5,
    base_type_name='INT8',
    name='INT8',    
)
INT8 = kbetype.INT8

_INT16_SPEC = _deftype.DataTypeSpec(
    id=6,
    base_type_name='INT16',
    name='INT16',    
)
INT16 = kbetype.INT16

_AVATAR_UID_SPEC = _deftype.DataTypeSpec(
    id=7,
    base_type_name='INT32',
    name='AVATAR_UID',    
)
AVATAR_UID = kbetype.INT32.alias('AVATAR_UID')

_INT64_SPEC = _deftype.DataTypeSpec(
    id=8,
    base_type_name='INT64',
    name='INT64',    
)
INT64 = kbetype.INT64

_STRING_SPEC = _deftype.DataTypeSpec(
    id=9,
    base_type_name='STRING',
    name='STRING',    
)
STRING = kbetype.STRING

_AVATAR_NAME_SPEC = _deftype.DataTypeSpec(
    id=10,
    base_type_name='UNICODE',
    name='AVATAR_NAME',    
)
AVATAR_NAME = kbetype.UNICODE.alias('AVATAR_NAME')

_FLOAT_SPEC = _deftype.DataTypeSpec(
    id=11,
    base_type_name='FLOAT',
    name='FLOAT',    
)
FLOAT = kbetype.FLOAT

_DOUBLE_SPEC = _deftype.DataTypeSpec(
    id=12,
    base_type_name='DOUBLE',
    name='DOUBLE',    
)
DOUBLE = kbetype.DOUBLE

_PYTHON_SPEC = _deftype.DataTypeSpec(
    id=13,
    base_type_name='PYTHON',
    name='PYTHON',    
)
PYTHON = kbetype.PYTHON

_PY_DICT_SPEC = _deftype.DataTypeSpec(
    id=14,
    base_type_name='PY_DICT',
    name='PY_DICT',    
)
PY_DICT = kbetype.PY_DICT

_PY_TUPLE_SPEC = _deftype.DataTypeSpec(
    id=15,
    base_type_name='PY_TUPLE',
    name='PY_TUPLE',    
)
PY_TUPLE = kbetype.PY_TUPLE

_PY_LIST_SPEC = _deftype.DataTypeSpec(
    id=16,
    base_type_name='PY_LIST',
    name='PY_LIST',    
)
PY_LIST = kbetype.PY_LIST

_ENTITYCALL_SPEC = _deftype.DataTypeSpec(
    id=17,
    base_type_name='ENTITYCALL',
    name='ENTITYCALL',    
)
ENTITYCALL = kbetype.ENTITYCALL

_BLOB_SPEC = _deftype.DataTypeSpec(
    id=18,
    base_type_name='BLOB',
    name='BLOB',    
)
BLOB = kbetype.BLOB

_VECTOR2_SPEC = _deftype.DataTypeSpec(
    id=19,
    base_type_name='VECTOR2',
    name='VECTOR2',    
)
VECTOR2 = kbetype.VECTOR2

_VECTOR3_SPEC = _deftype.DataTypeSpec(
    id=20,
    base_type_name='VECTOR3',
    name='VECTOR3',    
)
VECTOR3 = kbetype.VECTOR3

_VECTOR4_SPEC = _deftype.DataTypeSpec(
    id=21,
    base_type_name='VECTOR4',
    name='VECTOR4',    
)
VECTOR4 = kbetype.VECTOR4

_AVATAR_INFO_SPEC = _deftype.DataTypeSpec(
    id=22,
    base_type_name='FIXED_DICT',
    name='AVATAR_INFO',    
    module_name='',
    pairs={
        'name': AVATAR_NAME,
        'uid': AVATAR_UID,
        'dbid': DBID
    },
)
AVATAR_INFO = kbetype.FIXED_DICT.build(_AVATAR_INFO_SPEC.name, _AVATAR_INFO_SPEC.pairs)

_AVATAR_INFO_LIST_SPEC = _deftype.DataTypeSpec(
    id=23,
    base_type_name='ARRAY',
    name='AVATAR_INFO_LIST',    
    of=AVATAR_INFO,
)
AVATAR_INFO_LIST = kbetype.ARRAY.build(_AVATAR_INFO_LIST_SPEC.name, _AVATAR_INFO_LIST_SPEC.of)

_ARRAY_25_SPEC = _deftype.DataTypeSpec(
    id=25,
    base_type_name='ARRAY',
    name='ARRAY_25',    
    of=DBID,
)
ARRAY_25 = kbetype.ARRAY.build(_ARRAY_25_SPEC.name, _ARRAY_25_SPEC.of)

_AVATAR_DBIDS_SPEC = _deftype.DataTypeSpec(
    id=24,
    base_type_name='FIXED_DICT',
    name='AVATAR_DBIDS',    
    module_name='',
    pairs={
        'dbids': ARRAY_25
    },
)
AVATAR_DBIDS = kbetype.FIXED_DICT.build(_AVATAR_DBIDS_SPEC.name, _AVATAR_DBIDS_SPEC.pairs)

_NESTED_FIXED_DICT_SPEC = _deftype.DataTypeSpec(
    id=26,
    base_type_name='FIXED_DICT',
    name='NESTED_FIXED_DICT',    
    module_name='',
    pairs={
        'nested': AVATAR_INFO
    },
)
NESTED_FIXED_DICT = kbetype.FIXED_DICT.build(_NESTED_FIXED_DICT_SPEC.name, _NESTED_FIXED_DICT_SPEC.pairs)

_ARRAY_27_SPEC = _deftype.DataTypeSpec(
    id=27,
    base_type_name='ARRAY',
    name='ARRAY_27',    
    of=UINT16,
)
ARRAY_27 = kbetype.ARRAY.build(_ARRAY_27_SPEC.name, _ARRAY_27_SPEC.of)

TYPE_BY_ID = {
    1: UINT8,
    2: UINT16,
    3: DBID,
    4: UINT32,
    5: INT8,
    6: INT16,
    7: AVATAR_UID,
    8: INT64,
    9: STRING,
    10: AVATAR_NAME,
    11: FLOAT,
    12: DOUBLE,
    13: PYTHON,
    14: PY_DICT,
    15: PY_TUPLE,
    16: PY_LIST,
    17: ENTITYCALL,
    18: BLOB,
    19: VECTOR2,
    20: VECTOR3,
    21: VECTOR4,
    22: AVATAR_INFO,
    23: AVATAR_INFO_LIST,
    24: AVATAR_DBIDS,
    25: ARRAY_25,
    26: NESTED_FIXED_DICT,
    27: ARRAY_27
}

__all__ = (
    'UINT8', 'UINT16', 'DBID',
    'UINT32', 'INT8', 'INT16',
    'AVATAR_UID', 'INT64', 'STRING',
    'AVATAR_NAME', 'FLOAT', 'DOUBLE',
    'PYTHON', 'PY_DICT', 'PY_TUPLE',
    'PY_LIST', 'ENTITYCALL', 'BLOB',
    'VECTOR2', 'VECTOR3', 'VECTOR4',
    'AVATAR_INFO', 'AVATAR_INFO_LIST', 'ARRAY_25',
    'AVATAR_DBIDS', 'NESTED_FIXED_DICT', 'ARRAY_27'
)
