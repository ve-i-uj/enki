"""Generated module represents the entity "Avatar" of the file entities.xml."""

from __future__ import annotations

import logging

from descr.deftype import *
from enki.apps.clientapp.gameentity import (
    ClientEntityBaseRemoteCall,
    ClientEntityCellRemoteCall,
    ClientGameEntity,
    ClientGameEntityComponent,
)
from enki.apps.clientapp.layer.ilayer import INetLayer, KBEComponentEnum
from enki.kbetype import *
from enki.misc import devonly

from .components.Test import TestBase
from .components.TestNoBase import TestNoBaseBase

logger = logging.getLogger(__name__)


class _AvatarBaseRemoteCall(ClientEntityBaseRemoteCall):
    """Remote call to the BaseApp component of the entity."""

    def __init__(self, entity: AvatarBase) -> None:
        super().__init__(entity)


class _AvatarCellRemoteCall(ClientEntityCellRemoteCall):
    """Remote call to the CellApp component of the entity."""

    def __init__(self, entity: AvatarBase) -> None:
        super().__init__(entity)

    def dialog(self,
               int32_0: KBEInt32,
               uint32_1: KBEUInt32) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.CELL,
            "dialog",
            (int32_0, uint32_1 )
        )

    def jump(self) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.CELL,
            "jump",
            ()
        )

    def relive(self,
               uint8_0: KBEUInt8) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.CELL,
            "relive",
            (uint8_0, )
        )

    def requestPull(self) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.CELL,
            "requestPull",
            ()
        )

    def useTargetSkill(self,
                       int32_0: KBEInt32,
                       int32_1: KBEInt32) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.CELL,
            "useTargetSkill",
            (int32_0, int32_1 )
        )


class AvatarBase(ClientGameEntity):
    CLS_ID = 2

    def __init__(self, entity_id, is_player: bool, layer: INetLayer) -> None:
        super().__init__(entity_id, is_player, layer)

        self._cell = _AvatarCellRemoteCall(entity=self)
        self._base = _AvatarBaseRemoteCall(entity=self)
        self._position: Position = Position()
        self._direction: Direction = Direction()
        self._spaceID: KBEUInt32 = KBEUInt32(0)
        self._HP: KBEInt32 = KBEInt32(0)
        self._HP_Max: KBEInt32 = KBEInt32(0)
        self._MP: KBEInt32 = KBEInt32(0)
        self._MP_Max: KBEInt32 = KBEInt32(0)
        self._component1: TestBase = TestBase(self, owner_attr_id=16)
        self._component2: TestBase = TestBase(self, owner_attr_id=21)
        self._component3: TestNoBaseBase = TestNoBaseBase(self, owner_attr_id=22)
        self._forbids: KBEInt32 = KBEInt32(0)
        self._level: KBEUInt16 = KBEUInt16(0)
        self._modelID: KBEUInt32 = KBEUInt32(0)
        self._modelScale: KBEUInt8 = KBEUInt8(0)
        self._moveSpeed: KBEUInt8 = KBEUInt8(0)
        self._name: KBEUnicode = KBEUnicode()
        self._own_val: KBEUInt16 = KBEUInt16(0)
        self._spaceUType: KBEUInt32 = KBEUInt32(0)
        self._state: KBEInt8 = KBEInt8(0)
        self._subState: KBEUInt8 = KBEUInt8(0)
        self._uid: KBEUInt32 = KBEUInt32(0)
        self._utype: KBEUInt32 = KBEUInt32(0)

        self._components: dict[str, ClientGameEntityComponent] = {
            "component1": self._component1,
            "component2": self._component2,
            "component3": self._component3,
        }
        self._component_by_owner_attr_id = {
            comp.owner_attr_id: comp for comp in self._components.values()
        }

    @property
    def cell(self) -> _AvatarCellRemoteCall:
        return self._cell

    @property
    def base(self) -> _AvatarBaseRemoteCall:
        return self._base

    @property
    def className(self) -> str:
        return "Avatar"

    @property
    def position(self) -> Position:
        return self._position

    def set_position(self, old_value: Position) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    @property
    def direction(self) -> Direction:
        return self._direction

    def set_direction(self, old_value: Direction) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    @property
    def spaceID(self) -> KBEUInt32:
        return self._spaceID

    @property
    def HP(self) -> KBEInt32:
        return self._HP

    def set_HP(self, old_value: KBEInt32) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    @property
    def HP_Max(self) -> KBEInt32:
        return self._HP_Max

    def set_HP_Max(self, old_value: KBEInt32) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    @property
    def MP(self) -> KBEInt32:
        return self._MP

    def set_MP(self, old_value: KBEInt32) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    @property
    def MP_Max(self) -> KBEInt32:
        return self._MP_Max

    def set_MP_Max(self, old_value: KBEInt32) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    @property
    def component1(self) -> TestBase:
        return self._component1

    @property
    def component2(self) -> TestBase:
        return self._component2

    @property
    def component3(self) -> TestNoBaseBase:
        return self._component3

    @property
    def forbids(self) -> KBEInt32:
        return self._forbids

    def set_forbids(self, old_value: KBEInt32) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    @property
    def level(self) -> KBEUInt16:
        return self._level

    @property
    def modelID(self) -> KBEUInt32:
        return self._modelID

    def set_modelID(self, old_value: KBEUInt32) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    @property
    def modelScale(self) -> KBEUInt8:
        return self._modelScale

    def set_modelScale(self, old_value: KBEUInt8) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    @property
    def moveSpeed(self) -> KBEUInt8:
        return self._moveSpeed

    def set_moveSpeed(self, old_value: KBEUInt8) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    @property
    def name(self) -> KBEUnicode:
        return self._name

    def set_name(self, old_value: KBEUnicode) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    @property
    def own_val(self) -> KBEUInt16:
        return self._own_val

    def set_own_val(self, old_value: KBEUInt16) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    @property
    def spaceUType(self) -> KBEUInt32:
        return self._spaceUType

    @property
    def state(self) -> KBEInt8:
        return self._state

    def set_state(self, old_value: KBEInt8) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    @property
    def subState(self) -> KBEUInt8:
        return self._subState

    def set_subState(self, old_value: KBEUInt8) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    @property
    def uid(self) -> KBEUInt32:
        return self._uid

    def set_uid(self, old_value: KBEUInt32) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    @property
    def utype(self) -> KBEUInt32:
        return self._utype

    def set_utype(self, old_value: KBEUInt32) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    def dialog_addOption(self,
                         uint8_0: KBEUInt8,
                         uint32_1: KBEUInt32,
                         unicode_2: KBEUnicode,
                         int32_3: KBEInt32) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    def dialog_close(self) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    def dialog_setText(self,
                       unicode_0: KBEUnicode,
                       uint8_1: KBEUInt8,
                       uint32_2: KBEUInt32,
                       unicode_3: KBEUnicode) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    def onAddSkill(self,
                   int32_0: KBEInt32) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    def onJump(self) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    def onRemoveSkill(self,
                      int32_0: KBEInt32) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    def recvDamage(self,
                   int32_0: KBEInt32,
                   int32_1: KBEInt32,
                   int32_2: KBEInt32,
                   int32_3: KBEInt32) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())
