"""Generated types represent types of the file types.xml"""

import collections

from enki.net.kbeclient import kbetype
from enki import gedescr


ENTITY_SUBSTATE_SPEC = gedescr.DataTypeDescr(
    id=1,
    base_type_name='UINT8',
    name='ENTITY_SUBSTATE',
    kbetype=kbetype.UINT8.alias('ENTITY_SUBSTATE'),
)

UINT16_SPEC = gedescr.DataTypeDescr(
    id=2,
    base_type_name='UINT16',
    name='UINT16',
    kbetype=kbetype.UINT16,
)

UID_SPEC = gedescr.DataTypeDescr(
    id=3,
    base_type_name='UINT64',
    name='UID',
    kbetype=kbetype.UINT64.alias('UID'),
)

ENTITY_UTYPE_SPEC = gedescr.DataTypeDescr(
    id=4,
    base_type_name='UINT32',
    name='ENTITY_UTYPE',
    kbetype=kbetype.UINT32.alias('ENTITY_UTYPE'),
)

ENTITY_STATE_SPEC = gedescr.DataTypeDescr(
    id=5,
    base_type_name='INT8',
    name='ENTITY_STATE',
    kbetype=kbetype.INT8.alias('ENTITY_STATE'),
)

INT16_SPEC = gedescr.DataTypeDescr(
    id=6,
    base_type_name='INT16',
    name='INT16',
    kbetype=kbetype.INT16,
)

ENTITY_FORBIDS_SPEC = gedescr.DataTypeDescr(
    id=7,
    base_type_name='INT32',
    name='ENTITY_FORBIDS',
    kbetype=kbetype.INT32.alias('ENTITY_FORBIDS'),
)

INT64_SPEC = gedescr.DataTypeDescr(
    id=8,
    base_type_name='INT64',
    name='INT64',
    kbetype=kbetype.INT64,
)

STRING_SPEC = gedescr.DataTypeDescr(
    id=9,
    base_type_name='STRING',
    name='STRING',
    kbetype=kbetype.STRING,
)

UNICODE_SPEC = gedescr.DataTypeDescr(
    id=10,
    base_type_name='UNICODE',
    name='UNICODE',
    kbetype=kbetype.UNICODE,
)

FLOAT_SPEC = gedescr.DataTypeDescr(
    id=11,
    base_type_name='FLOAT',
    name='FLOAT',
    kbetype=kbetype.FLOAT,
)

DOUBLE_SPEC = gedescr.DataTypeDescr(
    id=12,
    base_type_name='DOUBLE',
    name='DOUBLE',
    kbetype=kbetype.DOUBLE,
)

UID1_SPEC = gedescr.DataTypeDescr(
    id=13,
    base_type_name='PYTHON',
    name='UID1',
    kbetype=kbetype.PYTHON.alias('UID1'),
)

PY_DICT_SPEC = gedescr.DataTypeDescr(
    id=14,
    base_type_name='PY_DICT',
    name='PY_DICT',
    kbetype=kbetype.PY_DICT,
)

PY_TUPLE_SPEC = gedescr.DataTypeDescr(
    id=15,
    base_type_name='PY_TUPLE',
    name='PY_TUPLE',
    kbetype=kbetype.PY_TUPLE,
)

PY_LIST_SPEC = gedescr.DataTypeDescr(
    id=16,
    base_type_name='PY_LIST',
    name='PY_LIST',
    kbetype=kbetype.PY_LIST,
)

ENTITYCALL_SPEC = gedescr.DataTypeDescr(
    id=17,
    base_type_name='ENTITYCALL',
    name='ENTITYCALL',
    kbetype=kbetype.ENTITYCALL,
)

BLOB_SPEC = gedescr.DataTypeDescr(
    id=18,
    base_type_name='BLOB',
    name='BLOB',
    kbetype=kbetype.BLOB,
)

VECTOR2_SPEC = gedescr.DataTypeDescr(
    id=19,
    base_type_name='VECTOR2',
    name='VECTOR2',
    kbetype=kbetype.VECTOR2,
)

DIRECTION3D_SPEC = gedescr.DataTypeDescr(
    id=20,
    base_type_name='VECTOR3',
    name='DIRECTION3D',
    kbetype=kbetype.VECTOR3.alias('DIRECTION3D'),
)

VECTOR4_SPEC = gedescr.DataTypeDescr(
    id=21,
    base_type_name='VECTOR4',
    name='VECTOR4',
    kbetype=kbetype.VECTOR4,
)

ENTITY_FORBID_COUNTER_SPEC = gedescr.DataTypeDescr(
    id=22,
    base_type_name='ARRAY',
    name='ENTITY_FORBID_COUNTER',
    of=ENTITY_STATE_SPEC.kbetype,
    kbetype=kbetype.ARRAY.build('ENTITY_FORBID_COUNTER', ENTITY_STATE_SPEC.kbetype),
)

ENTITYID_LIST_SPEC = gedescr.DataTypeDescr(
    id=23,
    base_type_name='ARRAY',
    name='ENTITYID_LIST',
    of=ENTITY_FORBIDS_SPEC.kbetype,
    kbetype=kbetype.ARRAY.build('ENTITYID_LIST', ENTITY_FORBIDS_SPEC.kbetype),
)

AVATAR_DATA_SPEC = gedescr.DataTypeDescr(
    id=24,
    base_type_name='FIXED_DICT',
    name='AVATAR_DATA',
    module_name='AVATAR_DATA.AVATAR_DATA_PICKLER',
    pairs=collections.OrderedDict([
        ('param1', ENTITY_STATE_SPEC.kbetype),
        ('param2', BLOB_SPEC.kbetype)
    ]),
    kbetype=kbetype.FIXED_DICT.build('AVATAR_DATA', collections.OrderedDict([
        ('param1', ENTITY_STATE_SPEC.kbetype),
        ('param2', BLOB_SPEC.kbetype)
    ])),
)

AVATAR_INFOS_SPEC = gedescr.DataTypeDescr(
    id=25,
    base_type_name='FIXED_DICT',
    name='AVATAR_INFOS',
    module_name='AVATAR_INFOS.avatar_info_inst',
    pairs=collections.OrderedDict([
        ('dbid', UID_SPEC.kbetype),
        ('name', UNICODE_SPEC.kbetype),
        ('roleType', ENTITY_SUBSTATE_SPEC.kbetype),
        ('level', UINT16_SPEC.kbetype),
        ('data', AVATAR_DATA_SPEC.kbetype)
    ]),
    kbetype=kbetype.FIXED_DICT.build('AVATAR_INFOS', collections.OrderedDict([
        ('dbid', UID_SPEC.kbetype),
        ('name', UNICODE_SPEC.kbetype),
        ('roleType', ENTITY_SUBSTATE_SPEC.kbetype),
        ('level', UINT16_SPEC.kbetype),
        ('data', AVATAR_DATA_SPEC.kbetype)
    ])),
)

ARRAY_27_SPEC = gedescr.DataTypeDescr(
    id=27,
    base_type_name='ARRAY',
    name='ARRAY_27',
    of=AVATAR_INFOS_SPEC.kbetype,
    kbetype=kbetype.ARRAY.build('ARRAY_27', AVATAR_INFOS_SPEC.kbetype),
)

AVATAR_INFOS_LIST_SPEC = gedescr.DataTypeDescr(
    id=26,
    base_type_name='FIXED_DICT',
    name='AVATAR_INFOS_LIST',
    module_name='AVATAR_INFOS.AVATAR_INFOS_LIST_PICKLER',
    pairs=collections.OrderedDict([
        ('values', ARRAY_27_SPEC.kbetype)
    ]),
    kbetype=kbetype.FIXED_DICT.build('AVATAR_INFOS_LIST', collections.OrderedDict([
        ('values', ARRAY_27_SPEC.kbetype)
    ])),
)

ARRAY_30_SPEC = gedescr.DataTypeDescr(
    id=30,
    base_type_name='ARRAY',
    name='ARRAY_30',
    of=INT64_SPEC.kbetype,
    kbetype=kbetype.ARRAY.build('ARRAY_30', INT64_SPEC.kbetype),
)

ARRAY_29_SPEC = gedescr.DataTypeDescr(
    id=29,
    base_type_name='ARRAY',
    name='ARRAY_29',
    of=ARRAY_30_SPEC.kbetype,
    kbetype=kbetype.ARRAY.build('ARRAY_29', ARRAY_30_SPEC.kbetype),
)

BAG_SPEC = gedescr.DataTypeDescr(
    id=28,
    base_type_name='FIXED_DICT',
    name='BAG',
    module_name='',
    pairs=collections.OrderedDict([
        ('values22', ARRAY_29_SPEC.kbetype)
    ]),
    kbetype=kbetype.FIXED_DICT.build('BAG', collections.OrderedDict([
        ('values22', ARRAY_29_SPEC.kbetype)
    ])),
)

EXAMPLES_SPEC = gedescr.DataTypeDescr(
    id=31,
    base_type_name='FIXED_DICT',
    name='EXAMPLES',
    module_name='',
    pairs=collections.OrderedDict([
        ('k1', INT64_SPEC.kbetype),
        ('k2', INT64_SPEC.kbetype)
    ]),
    kbetype=kbetype.FIXED_DICT.build('EXAMPLES', collections.OrderedDict([
        ('k1', INT64_SPEC.kbetype),
        ('k2', INT64_SPEC.kbetype)
    ])),
)

ARRAY_32_SPEC = gedescr.DataTypeDescr(
    id=32,
    base_type_name='ARRAY',
    name='ARRAY_32',
    of=ENTITY_FORBIDS_SPEC.kbetype,
    kbetype=kbetype.ARRAY.build('ARRAY_32', ENTITY_FORBIDS_SPEC.kbetype),
)

ENTITY_COMPONENT_33_SPEC = gedescr.DataTypeDescr(
    id=33,
    base_type_name='ENTITY_COMPONENT',
    name='ENTITY_COMPONENT_33',
    kbetype=kbetype.ENTITY_COMPONENT.alias('ENTITY_COMPONENT_33'),
)

ENTITY_COMPONENT_34_SPEC = gedescr.DataTypeDescr(
    id=34,
    base_type_name='ENTITY_COMPONENT',
    name='ENTITY_COMPONENT_34',
    kbetype=kbetype.ENTITY_COMPONENT.alias('ENTITY_COMPONENT_34'),
)

ENTITY_COMPONENT_35_SPEC = gedescr.DataTypeDescr(
    id=35,
    base_type_name='ENTITY_COMPONENT',
    name='ENTITY_COMPONENT_35',
    kbetype=kbetype.ENTITY_COMPONENT.alias('ENTITY_COMPONENT_35'),
)

TYPE_SPEC_BY_ID = {
    1: ENTITY_SUBSTATE_SPEC,
    2: UINT16_SPEC,
    3: UID_SPEC,
    4: ENTITY_UTYPE_SPEC,
    5: ENTITY_STATE_SPEC,
    6: INT16_SPEC,
    7: ENTITY_FORBIDS_SPEC,
    8: INT64_SPEC,
    9: STRING_SPEC,
    10: UNICODE_SPEC,
    11: FLOAT_SPEC,
    12: DOUBLE_SPEC,
    13: UID1_SPEC,
    14: PY_DICT_SPEC,
    15: PY_TUPLE_SPEC,
    16: PY_LIST_SPEC,
    17: ENTITYCALL_SPEC,
    18: BLOB_SPEC,
    19: VECTOR2_SPEC,
    20: DIRECTION3D_SPEC,
    21: VECTOR4_SPEC,
    22: ENTITY_FORBID_COUNTER_SPEC,
    23: ENTITYID_LIST_SPEC,
    24: AVATAR_DATA_SPEC,
    25: AVATAR_INFOS_SPEC,
    26: AVATAR_INFOS_LIST_SPEC,
    27: ARRAY_27_SPEC,
    28: BAG_SPEC,
    29: ARRAY_29_SPEC,
    30: ARRAY_30_SPEC,
    31: EXAMPLES_SPEC,
    32: ARRAY_32_SPEC,
    33: ENTITY_COMPONENT_33_SPEC,
    34: ENTITY_COMPONENT_34_SPEC,
    35: ENTITY_COMPONENT_35_SPEC
}

__all__ = (
    'ENTITY_SUBSTATE_SPEC', 'UINT16_SPEC', 'UID_SPEC',
    'ENTITY_UTYPE_SPEC', 'ENTITY_STATE_SPEC', 'INT16_SPEC',
    'ENTITY_FORBIDS_SPEC', 'INT64_SPEC', 'STRING_SPEC',
    'UNICODE_SPEC', 'FLOAT_SPEC', 'DOUBLE_SPEC',
    'UID1_SPEC', 'PY_DICT_SPEC', 'PY_TUPLE_SPEC',
    'PY_LIST_SPEC', 'ENTITYCALL_SPEC', 'BLOB_SPEC',
    'VECTOR2_SPEC', 'DIRECTION3D_SPEC', 'VECTOR4_SPEC',
    'ENTITY_FORBID_COUNTER_SPEC', 'ENTITYID_LIST_SPEC', 'AVATAR_DATA_SPEC',
    'AVATAR_INFOS_SPEC', 'ARRAY_27_SPEC', 'AVATAR_INFOS_LIST_SPEC',
    'ARRAY_30_SPEC', 'ARRAY_29_SPEC', 'BAG_SPEC',
    'EXAMPLES_SPEC', 'ARRAY_32_SPEC', 'ENTITY_COMPONENT_33_SPEC',
    'ENTITY_COMPONENT_34_SPEC', 'ENTITY_COMPONENT_35_SPEC', 'TYPE_SPEC_BY_ID'
)
