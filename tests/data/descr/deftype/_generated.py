"""Generated types represent types of the file types.xml"""

from typing import TypeAlias

from enki.kbetype import *

KBEEntitySubstate: TypeAlias = KBEUInt8
ENTITY_SUBSTATE: TypeAlias = UINT8

KBEUid: TypeAlias = KBEUInt64
UID: TypeAlias = UINT64

KBEEntityUtype: TypeAlias = KBEUInt32
ENTITY_UTYPE: TypeAlias = UINT32

KBEEntityState: TypeAlias = KBEInt8
ENTITY_STATE: TypeAlias = INT8

KBEEntityForbids: TypeAlias = KBEInt32
ENTITY_FORBIDS: TypeAlias = INT32

KBEUid1: TypeAlias = KBEPython
UID1: TypeAlias = PYTHON

KBEDirection3d: TypeAlias = KBEVector3
DIRECTION3D: TypeAlias = VECTOR3

KBEEntityStateArray: TypeAlias = KBEArray[KBEEntityState]


class ENTITY_FORBID_COUNTER(ARRAY[KBEEntityState, ENTITY_STATE]):
    """Декодер для типа массива ENTITY_STATE."""

    _element_decoder = ENTITY_STATE
    _kbe_type = KBEEntityStateArray

    @classmethod
    def get_kbe_type(cls) -> type[KBEEntityStateArray]:
        return cls._kbe_type

    @classmethod
    def _get_element_decoder(cls) -> type[ENTITY_STATE]:
        return cls._element_decoder

KBEEntityForbidsArray: TypeAlias = KBEArray[KBEEntityForbids]


class ENTITYID_LIST(ARRAY[KBEEntityForbids, ENTITY_FORBIDS]):
    """Декодер для типа массива ENTITY_FORBIDS."""

    _element_decoder = ENTITY_FORBIDS
    _kbe_type = KBEEntityForbidsArray

    @classmethod
    def get_kbe_type(cls) -> type[KBEEntityForbidsArray]:
        return cls._kbe_type

    @classmethod
    def _get_element_decoder(cls) -> type[ENTITY_FORBIDS]:
        return cls._element_decoder


@dataclass
class KBEAvatarDataFixedDict(KBEFixedDict):
    param1: KBEEntityState
    param2: KBEBlob


@dataclass
class KBEAvatarDataFixedDictDecoders(FixedDictDecoders):
    param1 = ENTITY_STATE
    param2 = BLOB


class AVATAR_DATA(FIXED_DICT[KBEAvatarDataFixedDict, KBEAvatarDataFixedDictDecoders]):
    _decoders = KBEAvatarDataFixedDictDecoders

    _kbe_type = KBEAvatarDataFixedDict

    @classmethod
    def get_kbe_type(cls) -> type[KBEAvatarDataFixedDict]:
        return cls._kbe_type


@dataclass
class KBEAvatarInfosFixedDict(KBEFixedDict):
    dbid: KBEUid
    name: KBEUnicode
    roleType: KBEEntitySubstate
    level: KBEUInt16
    data: KBEAvatarDataFixedDict


@dataclass
class KBEAvatarInfosFixedDictDecoders(FixedDictDecoders):
    dbid = UID
    name = UNICODE
    roleType = ENTITY_SUBSTATE
    level = UINT16
    data = AVATAR_DATA


class AVATAR_INFOS(FIXED_DICT[KBEAvatarInfosFixedDict, KBEAvatarInfosFixedDictDecoders]):
    _decoders = KBEAvatarInfosFixedDictDecoders

    _kbe_type = KBEAvatarInfosFixedDict

    @classmethod
    def get_kbe_type(cls) -> type[KBEAvatarInfosFixedDict]:
        return cls._kbe_type

KBEAvatarInfosFixedDictArray: TypeAlias = KBEArray[KBEAvatarInfosFixedDict]


class ARRAY_27(ARRAY[KBEAvatarInfosFixedDict, AVATAR_INFOS]):
    """Декодер для типа массива AVATAR_INFOS."""

    _element_decoder = AVATAR_INFOS
    _kbe_type = KBEAvatarInfosFixedDictArray

    @classmethod
    def get_kbe_type(cls) -> type[KBEAvatarInfosFixedDictArray]:
        return cls._kbe_type

    @classmethod
    def _get_element_decoder(cls) -> type[AVATAR_INFOS]:
        return cls._element_decoder


@dataclass
class KBEAvatarInfosListFixedDict(KBEFixedDict):
    values: KBEAvatarInfosFixedDictArray


@dataclass
class KBEAvatarInfosListFixedDictDecoders(FixedDictDecoders):
    values = ARRAY_27


class AVATAR_INFOS_LIST(FIXED_DICT[KBEAvatarInfosListFixedDict, KBEAvatarInfosListFixedDictDecoders]):
    _decoders = KBEAvatarInfosListFixedDictDecoders

    _kbe_type = KBEAvatarInfosListFixedDict

    @classmethod
    def get_kbe_type(cls) -> type[KBEAvatarInfosListFixedDict]:
        return cls._kbe_type

KBEInt64Array: TypeAlias = KBEArray[KBEInt64]


class ARRAY_30(ARRAY[KBEInt64, INT64]):
    """Декодер для типа массива INT64."""

    _element_decoder = INT64
    _kbe_type = KBEInt64Array

    @classmethod
    def get_kbe_type(cls) -> type[KBEInt64Array]:
        return cls._kbe_type

    @classmethod
    def _get_element_decoder(cls) -> type[INT64]:
        return cls._element_decoder

KBEInt64ArrayArray: TypeAlias = KBEArray[KBEInt64Array]


class ARRAY_29(ARRAY[KBEInt64Array, ARRAY_30]):
    """Декодер для типа массива ARRAY_30."""

    _element_decoder = ARRAY_30
    _kbe_type = KBEInt64ArrayArray

    @classmethod
    def get_kbe_type(cls) -> type[KBEInt64ArrayArray]:
        return cls._kbe_type

    @classmethod
    def _get_element_decoder(cls) -> type[ARRAY_30]:
        return cls._element_decoder


@dataclass
class KBEBagFixedDict(KBEFixedDict):
    values22: KBEInt64ArrayArray


@dataclass
class KBEBagFixedDictDecoders(FixedDictDecoders):
    values22 = ARRAY_29


class BAG(FIXED_DICT[KBEBagFixedDict, KBEBagFixedDictDecoders]):
    _decoders = KBEBagFixedDictDecoders

    _kbe_type = KBEBagFixedDict

    @classmethod
    def get_kbe_type(cls) -> type[KBEBagFixedDict]:
        return cls._kbe_type


@dataclass
class KBEExamplesFixedDict(KBEFixedDict):
    k1: KBEInt64
    k2: KBEInt64


@dataclass
class KBEExamplesFixedDictDecoders(FixedDictDecoders):
    k1 = INT64
    k2 = INT64


class EXAMPLES(FIXED_DICT[KBEExamplesFixedDict, KBEExamplesFixedDictDecoders]):
    _decoders = KBEExamplesFixedDictDecoders

    _kbe_type = KBEExamplesFixedDict

    @classmethod
    def get_kbe_type(cls) -> type[KBEExamplesFixedDict]:
        return cls._kbe_type


class ARRAY_32(ARRAY[KBEEntityForbids, ENTITY_FORBIDS]):
    """Декодер для типа массива ENTITY_FORBIDS."""

    _element_decoder = ENTITY_FORBIDS
    _kbe_type = KBEEntityForbidsArray

    @classmethod
    def get_kbe_type(cls) -> type[KBEEntityForbidsArray]:
        return cls._kbe_type

    @classmethod
    def _get_element_decoder(cls) -> type[ENTITY_FORBIDS]:
        return cls._element_decoder

KBEEntityComponent33: TypeAlias = EntityComponentData
ENTITY_COMPONENT_33: TypeAlias = ENTITY_COMPONENT

KBEEntityComponent34: TypeAlias = EntityComponentData
ENTITY_COMPONENT_34: TypeAlias = ENTITY_COMPONENT

KBEEntityComponent35: TypeAlias = EntityComponentData
ENTITY_COMPONENT_35: TypeAlias = ENTITY_COMPONENT


DECODER_BY_ID = {
    1: ENTITY_SUBSTATE,
    2: UINT16,
    3: UID,
    4: ENTITY_UTYPE,
    5: ENTITY_STATE,
    6: INT16,
    7: ENTITY_FORBIDS,
    8: INT64,
    9: STRING,
    10: UNICODE,
    11: FLOAT,
    12: DOUBLE,
    13: UID1,
    14: PY_DICT,
    15: PY_TUPLE,
    16: PY_LIST,
    17: ENTITYCALL,
    18: BLOB,
    19: VECTOR2,
    20: DIRECTION3D,
    21: VECTOR4,
    22: ENTITY_FORBID_COUNTER,
    23: ENTITYID_LIST,
    24: AVATAR_DATA,
    25: AVATAR_INFOS,
    26: AVATAR_INFOS_LIST,
    27: ARRAY_27,
    28: BAG,
    29: ARRAY_29,
    30: ARRAY_30,
    31: EXAMPLES,
    32: ARRAY_32,
    33: ENTITY_COMPONENT_33,
    34: ENTITY_COMPONENT_34,
    35: ENTITY_COMPONENT_35
}
