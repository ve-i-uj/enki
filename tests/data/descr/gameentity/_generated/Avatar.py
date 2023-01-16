"""Generated module represents the entity "Avatar" of the file entities.xml"""

from __future__ import annotations

import io
import logging
from typing import Optional

from enki import devonly
from enki.net.kbeclient.kbetype import Position, Direction, FixedDict, Array, \
    Vector2, Vector3, Vector4
from enki.layer import KBEComponentEnum, INetLayer
from enki.app.appl import App
from enki.app.gameentity import EntityBaseRemoteCall, EntityCellRemoteCall, \
    GameEntityComponent, GameEntity

from .components.Test import TestBase
from .components.TestNoBase import TestNoBaseBase
from ... import deftype

logger = logging.getLogger(__name__)


class _AvatarBaseRemoteCall(EntityBaseRemoteCall):
    """Remote call to the BaseApp component of the entity."""

    def __init__(self, entity: AvatarBase) -> None:
        super().__init__(entity)


class _AvatarCellRemoteCall(EntityCellRemoteCall):
    """Remote call to the CellApp component of the entity."""

    def __init__(self, entity: AvatarBase) -> None:
        super().__init__(entity)

    def dialog(self,
               entity_forbids_0: int,
               entity_utype_1: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.CELL,
            'dialog',
            (entity_forbids_0, entity_utype_1, )
        )

    def jump(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.CELL,
            'jump',
            ()
        )

    def relive(self,
               entity_substate_0: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.CELL,
            'relive',
            (entity_substate_0, )
        )

    def requestPull(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.CELL,
            'requestPull',
            ()
        )

    def useTargetSkill(self,
                       entity_forbids_0: int,
                       entity_forbids_1: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.CELL,
            'useTargetSkill',
            (entity_forbids_0, entity_forbids_1, )
        )


class AvatarBase(GameEntity):
    CLS_ID = 2

    def __init__(self, entity_id, is_player: bool, layer: INetLayer):
        super().__init__(entity_id, is_player, layer)

        self._cell = _AvatarCellRemoteCall(entity=self)
        self._base = _AvatarBaseRemoteCall(entity=self)
        self._position: Position = Position()
        self._direction: Direction = Direction()
        self._spaceID: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._HP: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self._HP_Max: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self._MP: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self._MP_Max: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self._component1: TestBase = TestBase(self, owner_attr_id=16)
        self._component2: TestBase = TestBase(self, owner_attr_id=21)
        self._component3: TestNoBaseBase = TestNoBaseBase(self, owner_attr_id=22)
        self._forbids: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self._level: int = deftype.UINT16_SPEC.kbetype.default
        self._modelID: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._modelScale: int = deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self._moveSpeed: int = deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self._name: str = deftype.UNICODE_SPEC.kbetype.default
        self._own_val: int = deftype.UINT16_SPEC.kbetype.default
        self._spaceUType: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._state: int = deftype.ENTITY_STATE_SPEC.kbetype.default
        self._subState: int = deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self._uid: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._utype: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default

        self._components: dict[str, GameEntityComponent] = {
            'component1': self._component1,
            'component2': self._component2,
            'component3': self._component3,
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
        return 'Avatar'

    @property
    def position(self) -> Position:
        return self._position

    def set_position(self, old_value: Position):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def direction(self) -> Direction:
        return self._direction

    def set_direction(self, old_value: Direction):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def spaceID(self) -> int:
        return self._spaceID

    @property
    def HP(self) -> int:
        return self._HP

    def set_HP(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def HP_Max(self) -> int:
        return self._HP_Max

    def set_HP_Max(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def MP(self) -> int:
        return self._MP

    def set_MP(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def MP_Max(self) -> int:
        return self._MP_Max

    def set_MP_Max(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

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
    def forbids(self) -> int:
        return self._forbids

    def set_forbids(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def level(self) -> int:
        return self._level

    @property
    def modelID(self) -> int:
        return self._modelID

    def set_modelID(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def modelScale(self) -> int:
        return self._modelScale

    def set_modelScale(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def moveSpeed(self) -> int:
        return self._moveSpeed

    def set_moveSpeed(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def name(self) -> str:
        return self._name

    def set_name(self, old_value: str):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def own_val(self) -> int:
        return self._own_val

    def set_own_val(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def spaceUType(self) -> int:
        return self._spaceUType

    @property
    def state(self) -> int:
        return self._state

    def set_state(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def subState(self) -> int:
        return self._subState

    def set_subState(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def uid(self) -> int:
        return self._uid

    def set_uid(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def utype(self) -> int:
        return self._utype

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
