"""Generated module represents the entity "Monster" of the file entities.xml"""

import collections
import io
import logging

from enki import kbetype, kbeclient, kbeentity, descr
from enki.misc import devonly

logger = logging.getLogger(__name__)


class _MonsterBaseEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the BaseApp component of the entity."""


class _MonsterCellEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the CellApp component of the entity."""


class MonsterBase(kbeentity.Entity):
    CLS_ID = 5

    def __init__(self, entity_id: int, entity_mgr: kbeentity.IEntityMgr):
        super().__init__(entity_id, entity_mgr)
        self._cell = _MonsterCellEntityRemoteCall(entity=self)
        self._base = _MonsterBaseEntityRemoteCall(entity=self)

        self._set_property_names = set(['position', 'direction', 'HP', 'HP_Max', 'MP', 'MP_Max', 'entityNO', 'forbids', 'modelID', 'modelScale', 'moveSpeed', 'name', 'state', 'subState', 'uid', 'utype'])

        self.__position: kbetype.Vector3Data = descr.deftype.DIRECTION3D_SPEC.kbetype.default
        self.__direction: kbetype.Vector3Data = descr.deftype.DIRECTION3D_SPEC.kbetype.default
        self.__spaceID: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self.__HP: int = descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self.__HP_Max: int = descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self.__MP: int = descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self.__MP_Max: int = descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self.__entityNO: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self.__forbids: int = descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self.__modelID: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self.__modelScale: int = descr.deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self.__moveSpeed: int = descr.deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self.__name: str = descr.deftype.UNICODE_SPEC.kbetype.default
        self.__state: int = descr.deftype.ENTITY_STATE_SPEC.kbetype.default
        self.__subState: int = descr.deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self.__uid: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self.__utype: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default

    @property
    def cell(self) -> _MonsterCellEntityRemoteCall:
        return self._cell

    @property
    def base(self) -> _MonsterBaseEntityRemoteCall:
        return self._base

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
    def HP(self) -> int:
        return self.__HP

    def set_HP(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def HP_Max(self) -> int:
        return self.__HP_Max

    def set_HP_Max(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def MP(self) -> int:
        return self.__MP

    def set_MP(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def MP_Max(self) -> int:
        return self.__MP_Max

    def set_MP_Max(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def entityNO(self) -> int:
        return self.__entityNO

    def set_entityNO(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def forbids(self) -> int:
        return self.__forbids

    def set_forbids(self, old_value: int):
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
    def state(self) -> int:
        return self.__state

    def set_state(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def subState(self) -> int:
        return self.__subState

    def set_subState(self, old_value: int):
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

    def recvDamage(self,
                   entity_forbids_0: int,
                   entity_forbids_1: int,
                   entity_forbids_2: int,
                   entity_forbids_3: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
