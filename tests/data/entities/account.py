"""The game logic of the "Account" entity."""

import logging

from enki.apps.clientapp.layer.ilayer import INetLayer
from enki.novalue import NoValue
from tests.data import descr

from ..descr.deftype import *

logger = logging.getLogger(__name__)


class Account(descr.gameentity.AccountBase):
    def __init__(self, entity_id, is_player: bool, layer: INetLayer) -> None:
        super().__init__(entity_id, is_player, layer)

        self._avatar_info_by_dbid: dict[KBEUid, KBEAvatarInfosFixedDict] = {}
        self._current_avatar_dbid: int = NoValue.NO_ID

    @property
    def current_avatar_dbid(self):
        return self._current_avatar_dbid

    def onReqAvatarList(self, avatar_infos_list_0: KBEAvatarInfosListFixedDict):
        dbid: int = NoValue.NO_ID
        for info in avatar_infos_list_0.values:
            self._avatar_info_by_dbid[info.dbid] = info
            dbid = info.dbid
        self._current_avatar_dbid = dbid

    def onCreateAvatarResult(
        self, uint8_0: KBEUInt8, avatar_infos_1: KBEAvatarInfosFixedDict
    ):
        logger.debug("[%s] ", self)
        dbid = avatar_infos_1.dbid
        self._avatar_info_by_dbid[dbid] = avatar_infos_1
        self._current_avatar_dbid = dbid
