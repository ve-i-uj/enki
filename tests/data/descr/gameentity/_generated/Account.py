"""Generated module represents the entity "Account" of the file entities.xml"""

from __future__ import annotations

import logging

from enki.misc import devonly
from enki.kbetype import *
from enki.apps.clientapp.layer.ilayer import KBEComponentEnum, INetLayer
from enki.apps.clientapp.gameentity import EntityBaseRemoteCall, EntityCellRemoteCall, \
    GameEntityComponent, GameEntity

from ...deftype import *

logger = logging.getLogger(__name__)


class _AccountBaseRemoteCall(EntityBaseRemoteCall):
    """Remote call to the BaseApp component of the entity."""

    def __init__(self, entity: AccountBase) -> None:
        super().__init__(entity)

    def reqAvatarList(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.BASE,
            'reqAvatarList',
            ()
        )

    def reqCreateAvatar(self,
                        uint8_0: KBEUInt8,
                        unicode_1: KBEUnicode):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.BASE,
            'reqCreateAvatar',
            (uint8_0, unicode_1, )
        )

    def reqRemoveAvatar(self,
                        unicode_0: KBEUnicode):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.BASE,
            'reqRemoveAvatar',
            (unicode_0, )
        )

    def reqRemoveAvatarDBID(self,
                            uint64_0: KBEUInt64):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.BASE,
            'reqRemoveAvatarDBID',
            (uint64_0, )
        )

    def selectAvatarGame(self,
                         uint64_0: KBEUInt64):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._entity.__call_remote_method__(
            KBEComponentEnum.BASE,
            'selectAvatarGame',
            (uint64_0, )
        )


class _AccountCellRemoteCall(EntityCellRemoteCall):
    """Remote call to the CellApp component of the entity."""

    def __init__(self, entity: AccountBase) -> None:
        super().__init__(entity)


class AccountBase(GameEntity):
    CLS_ID = 1

    def __init__(self, entity_id, is_player: bool, layer: INetLayer):
        super().__init__(entity_id, is_player, layer)

        self._cell = _AccountCellRemoteCall(entity=self)
        self._base = _AccountBaseRemoteCall(entity=self)
        self._position: Position = Position()
        self._direction: Direction = Direction()
        self._spaceID: KBEUInt32 = KBEUInt32(0)
        self._lastSelCharacter: KBEUInt64 = KBEUInt64(0)

        self._components: dict[str, GameEntityComponent] = {
        }
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
        return 'Account'

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
    def spaceID(self) -> KBEUInt32:
        return self._spaceID

    @property
    def lastSelCharacter(self) -> KBEUInt64:
        return self._lastSelCharacter

    def onCreateAvatarResult(self,
                             uint8_0: KBEUInt8,
                             avatar_infos_1: KBEAvatarInfosFixedDict):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def onRemoveAvatar(self,
                       uint64_0: KBEUInt64):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def onReqAvatarList(self,
                        avatar_infos_list_0: KBEAvatarInfosListFixedDict):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
