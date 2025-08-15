"""Менеджер по работе с глобальными данными конкретного объекта Space."""

import logging

from enki.apps.clientapp.layer import ilayer
from enki.apps.clientapp.layer.thlayer import IGameLayer

logger = logging.getLogger(__name__)


class SpaceDataMgr:
    @property
    def _game_layer(self) -> IGameLayer:
        return ilayer.get_game_layer()

    def set_data(self, space_id: int, key: str, value: str) -> None:
        self._game_layer.call_set_space_data(space_id, key, value)

    def del_data(self, space_id: int, key: str) -> None:
        self._game_layer.call_delete_space_data(space_id, key)
