"""Generated types represent types of the file types.xml"""

import collections

from enki import kbetype
from enki import dcdescr


UINT8_SPEC = dcdescr.DataTypeDescr(
    id=1,
    base_type_name='UINT8',
    name='UINT8',    
    kbetype=kbetype.UINT8,
)

UINT16_SPEC = dcdescr.DataTypeDescr(
    id=2,
    base_type_name='UINT16',
    name='UINT16',    
    kbetype=kbetype.UINT16,
)

DBID_SPEC = dcdescr.DataTypeDescr(
    id=3,
    base_type_name='UINT64',
    name='DBID',    
    kbetype=kbetype.UINT64.alias('DBID'),
)

UINT32_SPEC = dcdescr.DataTypeDescr(
    id=4,
    base_type_name='UINT32',
    name='UINT32',    
    kbetype=kbetype.UINT32,
)

INT8_SPEC = dcdescr.DataTypeDescr(
    id=5,
    base_type_name='INT8',
    name='INT8',    
    kbetype=kbetype.INT8,
)

INT16_SPEC = dcdescr.DataTypeDescr(
    id=6,
    base_type_name='INT16',
    name='INT16',    
    kbetype=kbetype.INT16,
)

AVATAR_UID_SPEC = dcdescr.DataTypeDescr(
    id=7,
    base_type_name='INT32',
    name='AVATAR_UID',    
    kbetype=kbetype.INT32.alias('AVATAR_UID'),
)

INT64_SPEC = dcdescr.DataTypeDescr(
    id=8,
    base_type_name='INT64',
    name='INT64',    
    kbetype=kbetype.INT64,
)

STRING_SPEC = dcdescr.DataTypeDescr(
    id=9,
    base_type_name='STRING',
    name='STRING',    
    kbetype=kbetype.STRING,
)

AVATAR_NAME_SPEC = dcdescr.DataTypeDescr(
    id=10,
    base_type_name='UNICODE',
    name='AVATAR_NAME',    
    kbetype=kbetype.UNICODE.alias('AVATAR_NAME'),
)

FLOAT_SPEC = dcdescr.DataTypeDescr(
    id=11,
    base_type_name='FLOAT',
    name='FLOAT',    
    kbetype=kbetype.FLOAT,
)

DOUBLE_SPEC = dcdescr.DataTypeDescr(
    id=12,
    base_type_name='DOUBLE',
    name='DOUBLE',    
    kbetype=kbetype.DOUBLE,
)

PYTHON_SPEC = dcdescr.DataTypeDescr(
    id=13,
    base_type_name='PYTHON',
    name='PYTHON',    
    kbetype=kbetype.PYTHON,
)

PY_DICT_SPEC = dcdescr.DataTypeDescr(
    id=14,
    base_type_name='PY_DICT',
    name='PY_DICT',    
    kbetype=kbetype.PY_DICT,
)

PY_TUPLE_SPEC = dcdescr.DataTypeDescr(
    id=15,
    base_type_name='PY_TUPLE',
    name='PY_TUPLE',    
    kbetype=kbetype.PY_TUPLE,
)

PY_LIST_SPEC = dcdescr.DataTypeDescr(
    id=16,
    base_type_name='PY_LIST',
    name='PY_LIST',    
    kbetype=kbetype.PY_LIST,
)

ENTITYCALL_SPEC = dcdescr.DataTypeDescr(
    id=17,
    base_type_name='ENTITYCALL',
    name='ENTITYCALL',    
    kbetype=kbetype.ENTITYCALL,
)

BLOB_SPEC = dcdescr.DataTypeDescr(
    id=18,
    base_type_name='BLOB',
    name='BLOB',    
    kbetype=kbetype.BLOB,
)

VECTOR2_SPEC = dcdescr.DataTypeDescr(
    id=19,
    base_type_name='VECTOR2',
    name='VECTOR2',    
    kbetype=kbetype.VECTOR2,
)

VECTOR3_SPEC = dcdescr.DataTypeDescr(
    id=20,
    base_type_name='VECTOR3',
    name='VECTOR3',    
    kbetype=kbetype.VECTOR3,
)

VECTOR4_SPEC = dcdescr.DataTypeDescr(
    id=21,
    base_type_name='VECTOR4',
    name='VECTOR4',    
    kbetype=kbetype.VECTOR4,
)

AVATAR_INFO_SPEC = dcdescr.DataTypeDescr(
    id=22,
    base_type_name='FIXED_DICT',
    name='AVATAR_INFO',    
    module_name='',
    pairs=collections.OrderedDict([
        ('name', AVATAR_NAME_SPEC.kbetype),
        ('uid', AVATAR_UID_SPEC.kbetype),
        ('dbid', DBID_SPEC.kbetype)
    ]),
    kbetype=kbetype.FIXED_DICT.build('AVATAR_INFO', collections.OrderedDict([
        ('name', AVATAR_NAME_SPEC.kbetype),
        ('uid', AVATAR_UID_SPEC.kbetype),
        ('dbid', DBID_SPEC.kbetype)
    ])),
)

AVATAR_INFO_LIST_SPEC = dcdescr.DataTypeDescr(
    id=23,
    base_type_name='ARRAY',
    name='AVATAR_INFO_LIST',    
    of=AVATAR_INFO_SPEC.kbetype,
    kbetype=kbetype.ARRAY.build('AVATAR_INFO_LIST', AVATAR_INFO_SPEC.kbetype),
)

ARRAY_25_SPEC = dcdescr.DataTypeDescr(
    id=25,
    base_type_name='ARRAY',
    name='ARRAY_25',    
    of=DBID_SPEC.kbetype,
    kbetype=kbetype.ARRAY.build('ARRAY_25', DBID_SPEC.kbetype),
)

AVATAR_DBIDS_SPEC = dcdescr.DataTypeDescr(
    id=24,
    base_type_name='FIXED_DICT',
    name='AVATAR_DBIDS',    
    module_name='',
    pairs=collections.OrderedDict([
        ('dbids', ARRAY_25_SPEC.kbetype)
    ]),
    kbetype=kbetype.FIXED_DICT.build('AVATAR_DBIDS', collections.OrderedDict([
        ('dbids', ARRAY_25_SPEC.kbetype)
    ])),
)

NESTED_FIXED_DICT_SPEC = dcdescr.DataTypeDescr(
    id=26,
    base_type_name='FIXED_DICT',
    name='NESTED_FIXED_DICT',    
    module_name='',
    pairs=collections.OrderedDict([
        ('nested', AVATAR_INFO_SPEC.kbetype)
    ]),
    kbetype=kbetype.FIXED_DICT.build('NESTED_FIXED_DICT', collections.OrderedDict([
        ('nested', AVATAR_INFO_SPEC.kbetype)
    ])),
)

ARRAY_27_SPEC = dcdescr.DataTypeDescr(
    id=27,
    base_type_name='ARRAY',
    name='ARRAY_27',    
    of=UINT16_SPEC.kbetype,
    kbetype=kbetype.ARRAY.build('ARRAY_27', UINT16_SPEC.kbetype),
)

TYPE_SPEC_BY_ID = {
    1: UINT8_SPEC,
    2: UINT16_SPEC,
    3: DBID_SPEC,
    4: UINT32_SPEC,
    5: INT8_SPEC,
    6: INT16_SPEC,
    7: AVATAR_UID_SPEC,
    8: INT64_SPEC,
    9: STRING_SPEC,
    10: AVATAR_NAME_SPEC,
    11: FLOAT_SPEC,
    12: DOUBLE_SPEC,
    13: PYTHON_SPEC,
    14: PY_DICT_SPEC,
    15: PY_TUPLE_SPEC,
    16: PY_LIST_SPEC,
    17: ENTITYCALL_SPEC,
    18: BLOB_SPEC,
    19: VECTOR2_SPEC,
    20: VECTOR3_SPEC,
    21: VECTOR4_SPEC,
    22: AVATAR_INFO_SPEC,
    23: AVATAR_INFO_LIST_SPEC,
    24: AVATAR_DBIDS_SPEC,
    25: ARRAY_25_SPEC,
    26: NESTED_FIXED_DICT_SPEC,
    27: ARRAY_27_SPEC
}

__all__ = (
    'UINT8_SPEC', 'UINT16_SPEC', 'DBID_SPEC',
    'UINT32_SPEC', 'INT8_SPEC', 'INT16_SPEC',
    'AVATAR_UID_SPEC', 'INT64_SPEC', 'STRING_SPEC',
    'AVATAR_NAME_SPEC', 'FLOAT_SPEC', 'DOUBLE_SPEC',
    'PYTHON_SPEC', 'PY_DICT_SPEC', 'PY_TUPLE_SPEC',
    'PY_LIST_SPEC', 'ENTITYCALL_SPEC', 'BLOB_SPEC',
    'VECTOR2_SPEC', 'VECTOR3_SPEC', 'VECTOR4_SPEC',
    'AVATAR_INFO_SPEC', 'AVATAR_INFO_LIST_SPEC', 'ARRAY_25_SPEC',
    'AVATAR_DBIDS_SPEC', 'NESTED_FIXED_DICT_SPEC', 'ARRAY_27_SPEC',
    'TYPE_SPEC_BY_ID'
)
