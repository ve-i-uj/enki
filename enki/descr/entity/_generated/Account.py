"""Generated module represents the entity "Account" of the file entities.xml"""

import collections
import logging

from enki import kbetype, bentity
from enki.misc import devonly

logger = logging.getLogger(__name__)


class AccountBase(bentity.Entity):
    CLS_ID = 1

    def __init__(self, entity_id: int):
        super().__init__(entity_id)
        self.__position: kbetype.Vector3Data = kbetype.Vector3Data(x=0.0, y=0.0, z=0.0)
        self.__direction: kbetype.Vector3Data = kbetype.Vector3Data(x=0.0, y=0.0, z=0.0)
        self.__spaceID: int = 0
        self.__test_default: int = 0
        self.__test_type_ARRAY_of_FIXED_DICT: kbetype.Array = kbetype.Array(of=FixedDict, type_name='AVATAR_INFO_LIST', initial_data=[])

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
    def test_default(self) -> int:
        return self.__test_default

    @property
    def test_type_ARRAY_of_FIXED_DICT(self) -> kbetype.Array:
        return self.__test_type_ARRAY_of_FIXED_DICT
