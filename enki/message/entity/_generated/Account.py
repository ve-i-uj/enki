"""Generated module represents the entity "Account" of the file entities.xml"""

import logging

from enki import kbetype
from enki.message import deftype
from enki.misc import devonly

from .. import _entity

logger = logging.getLogger(__name__)


class AccountBase(_entity.Entity):
    ID = 1

    def __init__(self):
        super().__init__()
        self.__position: kbetype.Vector3Data = deftype.VECTOR3_SPEC.kbetype.default
        self.__direction: kbetype.Vector3Data = deftype.VECTOR3_SPEC.kbetype.default
        self.__spaceID: int = deftype.UINT32_SPEC.kbetype.default
        self.__test_alias_DBID: int = 11
        self.__test_type_ARRAY_of_FIXED_DICT: list = deftype.AVATAR_INFO_LIST_SPEC.kbetype.default
        self.__test_type_FIXED_DICT: dict = deftype.AVATAR_INFO_SPEC.kbetype.default
        self.__test_type_PYTHON: object = deftype.PYTHON_SPEC.kbetype.default
        self.__test_type_VECTOR2: kbetype.Vector2Data = deftype.VECTOR2_SPEC.kbetype.default
        self.__test_type_VECTOR3: kbetype.Vector3Data = deftype.VECTOR3_SPEC.kbetype.default
        self.__test_type_VECTOR4: kbetype.Vector4Data = deftype.VECTOR4_SPEC.kbetype.default

    @property
    def position(self) -> kbetype.Vector3Data:
        return self.__position

    @property
    def direction(self) -> kbetype.Vector3Data:
        return self.__direction

    @property
    def spaceID(self) -> int:
        return self.__spaceID

    @property
    def test_alias_DBID(self) -> int:
        return self.__test_alias_DBID

    @property
    def test_type_ARRAY_of_FIXED_DICT(self) -> list:
        return self.__test_type_ARRAY_of_FIXED_DICT

    @property
    def test_type_FIXED_DICT(self) -> dict:
        return self.__test_type_FIXED_DICT

    @property
    def test_type_PYTHON(self) -> object:
        return self.__test_type_PYTHON

    @property
    def test_type_VECTOR2(self) -> kbetype.Vector2Data:
        return self.__test_type_VECTOR2

    @property
    def test_type_VECTOR3(self) -> kbetype.Vector3Data:
        return self.__test_type_VECTOR3

    @property
    def test_type_VECTOR4(self) -> kbetype.Vector4Data:
        return self.__test_type_VECTOR4

    def resp_get_avatars(self,
                         avatar_dbids: dict,
                         array_27: list):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
