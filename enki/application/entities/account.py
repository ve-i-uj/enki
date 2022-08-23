"""The game logic of the "Account" entity."""

from enki import kbetype, descr
from enki import kbeentity


class Account(descr.entity.AccountBase):

    def __init__(self, entity_id: int, entity_mgr: kbeentity.IEntityMgr):
        super().__init__(entity_id, entity_mgr)
        self._avatars = {}

    def onReqAvatarList(self, avatar_infos_list_0: kbetype.PluginFixedDict):
        super().onReqAvatarList(avatar_infos_list_0)
        for info in avatar_infos_list_0['values']:
            dbid = info['dbid']
            self._avatars[dbid] = info

    def onCreateAvatarResult(self, entity_substate_0: int, avatar_infos_1: kbetype.PluginFixedDict):
        super().onCreateAvatarResult(entity_substate_0, avatar_infos_1)
        self.base.reqAvatarList()
