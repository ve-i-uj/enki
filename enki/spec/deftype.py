"""Generated types represent types of the file types.xml"""

from enki import deftype

UINT8 = deftype.DataTypeSpec(
    id=1,
    base_type_name='UINT8',
    name='UINT8',    
    module_name=None,
    pairs=None,
    of=None
)

UINT16 = deftype.DataTypeSpec(
    id=2,
    base_type_name='UINT16',
    name='UINT16',    
    module_name=None,
    pairs=None,
    of=None
)

DBID = deftype.DataTypeSpec(
    id=3,
    base_type_name='UINT64',
    name='DBID',    
    module_name=None,
    pairs=None,
    of=None
)

UINT32 = deftype.DataTypeSpec(
    id=4,
    base_type_name='UINT32',
    name='UINT32',    
    module_name=None,
    pairs=None,
    of=None
)

INT8 = deftype.DataTypeSpec(
    id=5,
    base_type_name='INT8',
    name='INT8',    
    module_name=None,
    pairs=None,
    of=None
)

INT16 = deftype.DataTypeSpec(
    id=6,
    base_type_name='INT16',
    name='INT16',    
    module_name=None,
    pairs=None,
    of=None
)

AVATAR_UID = deftype.DataTypeSpec(
    id=7,
    base_type_name='INT32',
    name='AVATAR_UID',    
    module_name=None,
    pairs=None,
    of=None
)

INT64 = deftype.DataTypeSpec(
    id=8,
    base_type_name='INT64',
    name='INT64',    
    module_name=None,
    pairs=None,
    of=None
)

STRING = deftype.DataTypeSpec(
    id=9,
    base_type_name='STRING',
    name='STRING',    
    module_name=None,
    pairs=None,
    of=None
)

AVATAR_NAME = deftype.DataTypeSpec(
    id=10,
    base_type_name='UNICODE',
    name='AVATAR_NAME',    
    module_name=None,
    pairs=None,
    of=None
)

FLOAT = deftype.DataTypeSpec(
    id=11,
    base_type_name='FLOAT',
    name='FLOAT',    
    module_name=None,
    pairs=None,
    of=None
)

DOUBLE = deftype.DataTypeSpec(
    id=12,
    base_type_name='DOUBLE',
    name='DOUBLE',    
    module_name=None,
    pairs=None,
    of=None
)

PYTHON = deftype.DataTypeSpec(
    id=13,
    base_type_name='PYTHON',
    name='PYTHON',    
    module_name=None,
    pairs=None,
    of=None
)

PY_DICT = deftype.DataTypeSpec(
    id=14,
    base_type_name='PY_DICT',
    name='PY_DICT',    
    module_name=None,
    pairs=None,
    of=None
)

PY_TUPLE = deftype.DataTypeSpec(
    id=15,
    base_type_name='PY_TUPLE',
    name='PY_TUPLE',    
    module_name=None,
    pairs=None,
    of=None
)

PY_LIST = deftype.DataTypeSpec(
    id=16,
    base_type_name='PY_LIST',
    name='PY_LIST',    
    module_name=None,
    pairs=None,
    of=None
)

ENTITYCALL = deftype.DataTypeSpec(
    id=17,
    base_type_name='ENTITYCALL',
    name='ENTITYCALL',    
    module_name=None,
    pairs=None,
    of=None
)

BLOB = deftype.DataTypeSpec(
    id=18,
    base_type_name='BLOB',
    name='BLOB',    
    module_name=None,
    pairs=None,
    of=None
)

VECTOR2 = deftype.DataTypeSpec(
    id=19,
    base_type_name='VECTOR2',
    name='VECTOR2',    
    module_name=None,
    pairs=None,
    of=None
)

VECTOR3 = deftype.DataTypeSpec(
    id=20,
    base_type_name='VECTOR3',
    name='VECTOR3',    
    module_name=None,
    pairs=None,
    of=None
)

VECTOR4 = deftype.DataTypeSpec(
    id=21,
    base_type_name='VECTOR4',
    name='VECTOR4',    
    module_name=None,
    pairs=None,
    of=None
)

AVATAR_INFO = deftype.DataTypeSpec(
    id=22,
    base_type_name='FIXED_DICT',
    name='AVATAR_INFO',    
    module_name='',
    pairs={'name': 10, 'uid': 7, 'dbid': 3},
    of=None
)

AVATAR_INFO_LIST = deftype.DataTypeSpec(
    id=23,
    base_type_name='ARRAY',
    name='AVATAR_INFO_LIST',    
    module_name=None,
    pairs=None,
    of=22
)

AVATAR_DBIDS = deftype.DataTypeSpec(
    id=24,
    base_type_name='FIXED_DICT',
    name='AVATAR_DBIDS',    
    module_name='',
    pairs={'dbids': 25},
    of=None
)

ARRAY_25 = deftype.DataTypeSpec(
    id=25,
    base_type_name='ARRAY',
    name='ARRAY_25',    
    module_name=None,
    pairs=None,
    of=3
)

ARRAY_26 = deftype.DataTypeSpec(
    id=26,
    base_type_name='ARRAY',
    name='ARRAY_26',    
    module_name=None,
    pairs=None,
    of=2
)
