"""Generated module represents the entity "NPC" of the file entities.xml"""

import collections
import io
import logging

from enki import kbetype, kbeclient, kbeentity, descr
from enki.misc import devonly

logger = logging.getLogger(__name__)


class _NPCBaseEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the BaseApp component of the entity."""


class _NPCCellEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the CellApp component of the entity."""


class NPCBase(kbeentity.Entity):
    CLS_ID = 6

    def __init__(self, entity_id: int, entity_mgr: kbeentity.IEntityMgr):
        super().__init__(entity_id, entity_mgr)
        self._cell = _NPCCellEntityRemoteCall(entity=self)
        self._base = _NPCBaseEntityRemoteCall(entity=self)

        self._set_property_names = set(['position', 'direction', 'entityNO', 'modelID', 'modelScale', 'moveSpeed', 'name', 'uid', 'utype'])

        self.__position: kbetype.Vector3Data = descr.deftype.DIRECTION3D_SPEC.kbetype.default
        self.__direction: kbetype.Vector3Data = descr.deftype.DIRECTION3D_SPEC.kbetype.default
        self.__spaceID: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self.__entityNO: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self.__modelID: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self.__modelScale: int = descr.deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self.__moveSpeed: int = descr.deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self.__name: str = descr.deftype.UNICODE_SPEC.kbetype.default
        self.__uid: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self.__utype: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default

    @property
    def position(self) -> kbetype.Vector3Data:
        return self.__position

    def set_position(self, old_value: kbetype.Vector3Data):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def direction(self) -> kbetype.Vector3Data:
        return self.__direction

    def set_direction(self, old_value: kbetype.Vector3Data):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def spaceID(self) -> int:
        return self.__spaceID

    @property
    def entityNO(self) -> int:
        return self.__entityNO

    def set_entityNO(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def modelID(self) -> int:
        return self.__modelID

    def set_modelID(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def modelScale(self) -> int:
        return self.__modelScale

    def set_modelScale(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def moveSpeed(self) -> int:
        return self.__moveSpeed

    def set_moveSpeed(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def name(self) -> str:
        return self.__name

    def set_name(self, old_value: str):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def uid(self) -> int:
        return self.__uid

    def set_uid(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def utype(self) -> int:
        return self.__utype

    def set_utype(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
