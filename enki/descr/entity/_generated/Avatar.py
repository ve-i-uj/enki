"""Generated module represents the entity "Avatar" of the file entities.xml"""

import collections
import io
import logging

from enki import kbetype, kbeclient, kbeentity, descr
from enki.misc import devonly

logger = logging.getLogger(__name__)


class _AvatarBaseEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the BaseApp component of the entity."""


class _AvatarCellEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the CellApp component of the entity."""

    def dialog(self, arg_0: int, arg_1: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID ??
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(11003))
        io_obj.write(descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.encode(arg_0))
        io_obj.write(descr.deftype.ENTITY_UTYPE_SPEC.kbetype.encode(arg_1))
        
        msg = kbeclient.Message(
            spec=descr.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)

    def jump(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID ??
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(5))
        
        msg = kbeclient.Message(
            spec=descr.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)

    def relive(self, arg_0: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID ??
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(4))
        io_obj.write(descr.deftype.ENTITY_SUBSTATE_SPEC.kbetype.encode(arg_0))
        
        msg = kbeclient.Message(
            spec=descr.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)

    def requestPull(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID ??
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(11))
        
        msg = kbeclient.Message(
            spec=descr.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)

    def useTargetSkill(self, arg_0: int, arg_1: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID ??
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(11001))
        io_obj.write(descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.encode(arg_0))
        io_obj.write(descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.encode(arg_1))
        
        msg = kbeclient.Message(
            spec=descr.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)


class AvatarBase(kbeentity.Entity):
    CLS_ID = 2

    def __init__(self, entity_id: int, entity_mgr: kbeentity.IEntityMgr):
        super().__init__(entity_id, entity_mgr)
        self._cell = _AvatarCellEntityRemoteCall(entity=self)
        self._base = _AvatarBaseEntityRemoteCall(entity=self)

        self._set_property_names = set(['position', 'direction', 'HP', 'HP_Max', 'MP', 'MP_Max', 'forbids', 'modelID', 'modelScale', 'moveSpeed', 'name', 'own_val', 'state', 'subState', 'uid', 'utype'])

        self.__position: kbetype.Vector3Data = descr.deftype.DIRECTION3D_SPEC.kbetype.default
        self.__direction: kbetype.Vector3Data = descr.deftype.DIRECTION3D_SPEC.kbetype.default
        self.__spaceID: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self.__HP: int = descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self.__HP_Max: int = descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self.__MP: int = descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self.__MP_Max: int = descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self.__component1: str = descr.deftype.ENTITY_COMPONENT_33_SPEC.kbetype.default
        self.__component2: str = descr.deftype.ENTITY_COMPONENT_34_SPEC.kbetype.default
        self.__component3: str = descr.deftype.ENTITY_COMPONENT_35_SPEC.kbetype.default
        self.__forbids: int = descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self.__level: int = descr.deftype.UINT16_SPEC.kbetype.default
        self.__modelID: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self.__modelScale: int = descr.deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self.__moveSpeed: int = descr.deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self.__name: str = descr.deftype.UNICODE_SPEC.kbetype.default
        self.__own_val: int = descr.deftype.UINT16_SPEC.kbetype.default
        self.__spaceUType: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self.__state: int = descr.deftype.ENTITY_STATE_SPEC.kbetype.default
        self.__subState: int = descr.deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
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
    def component1(self) -> str:
        return self.__component1

    @property
    def component2(self) -> str:
        return self.__component2

    @property
    def component3(self) -> str:
        return self.__component3

    @property
    def forbids(self) -> int:
        return self.__forbids

    def set_forbids(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def level(self) -> int:
        return self.__level

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
    def own_val(self) -> int:
        return self.__own_val

    def set_own_val(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def spaceUType(self) -> int:
        return self.__spaceUType

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

    def dialog_addOption(self,
                         entity_substate_0: int,
                         entity_utype_1: int,
                         unicode_2: str,
                         entity_forbids_3: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def dialog_close(self):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def dialog_setText(self,
                       unicode_0: str,
                       entity_substate_1: int,
                       entity_utype_2: int,
                       unicode_3: str):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def onAddSkill(self,
                   entity_forbids_0: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def onJump(self):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def onRemoveSkill(self,
                      entity_forbids_0: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def recvDamage(self,
                   entity_forbids_0: int,
                   entity_forbids_1: int,
                   entity_forbids_2: int,
                   entity_forbids_3: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
