"""The game logic of the "Account" entity."""

from enki.layer import INetLayer
from enki.net.kbeclient.kbetype import FixedDict


from tests.data import descr


class Account(descr.gameentity.AccountBase):

    def __init__(self, entity_id, is_player: bool, layer: INetLayer):
        super().__init__(entity_id, is_player, layer)
        self._avatars = {}

    def onReqAvatarList(self, avatar_infos_list_0: FixedDict):
        super().onReqAvatarList(avatar_infos_list_0)
        for info in avatar_infos_list_0['values']:
            dbid = info['dbid']
            self._avatars[dbid] = info

    def onCreateAvatarResult(self, entity_substate_0: int, avatar_infos_1: FixedDict):
        super().onCreateAvatarResult(entity_substate_0, avatar_infos_1)
        self.base.reqAvatarList()
