"""Generated module represents the entity "Account" of the file entities.xml."""

from __future__ import annotations

import logging

from descr import deftype
from enki.apps.clientapp.gameentity import (
    EntityBaseRemoteCall,
    EntityCellRemoteCall,
    GameEntity,
    GameEntityComponent,
)
from enki.apps.clientapp.layer.ilayer import INetLayer, KBEComponentEnum
from enki.core.kbetype import (
    Direction,
    FixedDict,
    Position,
)
from enki.misc import devonly

logger = logging.getLogger(__name__)


class _AccountBaseRemoteCall(EntityBaseRemoteCall):
    """Remote call to the BaseApp component of the entity."""

    def __init__(self, entity: AccountBase) -> None:
        super().__init__(entity)

    def reqAvatarList(self) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.BASE, "reqAvatarList", ()
        )

    def reqCreateAvatar(self, entity_substate_0: int, unicode_1: str) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.BASE,
            "reqCreateAvatar",
            (entity_substate_0, unicode_1),
        )

    def reqRemoveAvatar(self, unicode_0: str) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.BASE, "reqRemoveAvatar", (unicode_0,)
        )

    def reqRemoveAvatarDBID(self, uid_0: int) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.BASE, "reqRemoveAvatarDBID", (uid_0,)
        )

    def selectAvatarGame(self, uid_0: int) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.BASE, "selectAvatarGame", (uid_0,)
        )


class _AccountCellRemoteCall(EntityCellRemoteCall):
    """Remote call to the CellApp component of the entity."""

    def __init__(self, entity: AccountBase) -> None:
        super().__init__(entity)


class AccountBase(GameEntity):
    CLS_ID = 1

    def __init__(self, entity_id, is_player: bool, layer: INetLayer) -> None:
        super().__init__(entity_id, is_player, layer)

        self._cell = _AccountCellRemoteCall(entity=self)
        self._base = _AccountBaseRemoteCall(entity=self)
        self._position: Position = Position()
        self._direction: Direction = Direction()
        self._spaceID: int = deftype.ENTITY_UTYPE_SPEC.default_python_value
        self._lastSelCharacter: int = deftype.UID_SPEC.default_python_value

        self._components: dict[str, GameEntityComponent] = {}
        self._component_by_owner_attr_id = {
            comp.owner_attr_id: comp for comp in self._components.values()
        }

    @property
    def cell(self) -> _AccountCellRemoteCall:
        return self._cell

    @property
    def base(self) -> _AccountBaseRemoteCall:
        return self._base

    @property
    def className(self) -> str:
        return "Account"

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
    def spaceID(self) -> int:
        return self._spaceID

    @property
    def lastSelCharacter(self) -> int:
        return self._lastSelCharacter

    def onCreateAvatarResult(
        self, entity_substate_0: int, avatar_infos_1: FixedDict
    ) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    def onRemoveAvatar(self, uid_0: int) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())

    def onReqAvatarList(self, avatar_infos_list_0: FixedDict) -> None:
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())
