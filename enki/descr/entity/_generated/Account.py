"""Generated module represents the entity "Account" of the file entities.xml"""

import logging

from enki import kbetype
from enki.misc import devonly

from .. import _entity

logger = logging.getLogger(__name__)


class AccountBase(_entity.Entity):
    CLS_ID = 1

    def __init__(self, entity_id: int):
        super().__init__(entity_id)
        self.__position: kbetype.Vector3Data = kbetype.Vector3Data(x=0.0, y=0.0, z=0.0)
        self.__direction: kbetype.Vector3Data = kbetype.Vector3Data(x=0.0, y=0.0, z=0.0)
        self.__spaceID: int = 0
        self.__test_alias_DBID: int = 11
        self.__test_type_ARRAY_of_FIXED_DICT: list = []
        self.__test_type_FIXED_DICT: dict = {'name': '', 'uid': 0, 'dbid': 0}
        self.__test_type_PYTHON: object = object()
        self.__test_type_VECTOR2: kbetype.Vector2Data = kbetype.Vector2Data(x=0.0, y=0.0)
        self.__test_type_VECTOR3: kbetype.Vector3Data = kbetype.Vector3Data(x=0.0, y=0.0, z=0.0)
        self.__test_type_VECTOR4: kbetype.Vector4Data = kbetype.Vector4Data(x=0.0, y=0.0, z=0.0, w=0.0)

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
