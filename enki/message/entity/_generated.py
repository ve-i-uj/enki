"""Generated classes represent entity of the file entities.xml"""

import logging

from . import _entity
from .. import deftype

from enki import kbetype
from enki.misc import devonly

logger = logging.getLogger(__name__)


class Account(_entity.Entity):
    ID = 1

    def __init__(self):
        # Выставляется дефолтное значение, если есть (или оно должно придти с сервера)
        self.__position: kbetype.Vector3 = None

    @property
    # @_entity.property_spec(deftype.VECTOR3)
    def position(self) -> deftype.VECTOR3:
        return self.__position

    @property
    def direction(self) -> deftype.VECTOR3:
        return deftype.VECTOR3.default

    @property
    def spaceID(self) -> deftype.UINT32:
        return deftype.UINT32.default

    @property
    def test_alias_DBID(self) -> deftype.DBID:
        return deftype.DBID.default

    @property
    def test_type_ARRAY_of_FIXED_DICT(self) -> deftype.AVATAR_INFO_LIST:
        return deftype.AVATAR_INFO_LIST.default

    @property
    def test_type_FIXED_DICT(self) -> deftype.AVATAR_INFO:
        return deftype.AVATAR_INFO.default

    @property
    def test_type_PYTHON(self) -> deftype.PYTHON:
        return deftype.PYTHON.default

    @property
    def test_type_VECTOR2(self) -> deftype.VECTOR2:
        return deftype.VECTOR2.default

    @property
    def test_type_VECTOR3(self) -> deftype.VECTOR3:
        return deftype.VECTOR3.default

    @property
    def test_type_VECTOR4(self) -> deftype.VECTOR4:
        return deftype.VECTOR4.default

    def resp_get_avatars(self,
                         avatar_dbids: deftype.AVATAR_DBIDS,
                         array_27: deftype.ARRAY_27):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())


ENTITY_CLS_BY_ID = {
    1: Account
}

__all__ = (
    'Account', 'ENTITY_CLS_BY_ID'
)
