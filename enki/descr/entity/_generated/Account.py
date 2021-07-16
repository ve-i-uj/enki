"""Generated module represents the entity "Account" of the file entities.xml"""

import collections
import logging

from enki import kbetype, bentity, descr
from enki.misc import devonly

logger = logging.getLogger(__name__)


class AccountBase(bentity.Entity):
    CLS_ID = 1

    def __init__(self, entity_id: int):
        super().__init__(entity_id)
        self.__position: kbetype.Vector3Data = descr.deftype.VECTOR3_SPEC.kbetype.default
        self.__direction: kbetype.Vector3Data = descr.deftype.VECTOR3_SPEC.kbetype.default
        self.__spaceID: int = descr.deftype.UINT32_SPEC.kbetype.default
        self.__test_type_ARRAY_of_FIXED_DICT: kbetype.Array = descr.deftype.AVATAR_INFO_LIST_SPEC.kbetype.default

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
    def test_type_ARRAY_of_FIXED_DICT(self) -> kbetype.Array:
        return self.__test_type_ARRAY_of_FIXED_DICT

    def resp_get_avatars(self,
                         avatar_dbids: kbetype.FixedDict,
                         array_27: kbetype.Array):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
