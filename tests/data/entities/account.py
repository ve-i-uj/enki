"""The game logic of the "Account" entity."""

from enki import settings
from enki.layer import INetLayer
from enki.net.kbeclient.kbetype import FixedDict


from tests.data import descr


class Account(descr.gameentity.AccountBase):

    def __init__(self, entity_id, is_player: bool, layer: INetLayer):
        super().__init__(entity_id, is_player, layer)
        self._avatar_info_by_dbid = {}
        self._current_avatar_dbid: int = settings.NO_ID

    @property
    def current_avatar_dbid(self):
        return self._current_avatar_dbid

    def onReqAvatarList(self, avatar_infos_list_0: FixedDict):
        super().onReqAvatarList(avatar_infos_list_0)
        dbid: int = settings.NO_ID
        for info in avatar_infos_list_0['values']:
            dbid = info['dbid']
            self._avatar_info_by_dbid[dbid] = info
        self._current_avatar_dbid = dbid

    def onCreateAvatarResult(self, entity_substate_0: int, avatar_infos_1: FixedDict):
        super().onCreateAvatarResult(entity_substate_0, avatar_infos_1)
        dbid = avatar_infos_1['dbid']
        self._avatar_info_by_dbid[dbid] = avatar_infos_1
        self._current_avatar_dbid = dbid
