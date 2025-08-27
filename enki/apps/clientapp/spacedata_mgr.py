"""Менеджер по работе с глобальными данными конкретного объекта Space."""

import logging

from enki.apps.clientapp.layer import ilayer
from enki.apps.clientapp.layer.thlayer import IGameLayer

logger = logging.getLogger(__name__)

# TODO: [2025-08-15 13:56 burov_alexey@mail.ru]:
# Скорей всего это должно быть прямо в приложении, которое отправляет это в
# игру. SpaceData - это уже игровая-движковая логика (там же в модуле KBEngine
# даже колбэки есть, вроде). А эта штука скорей всего не нужна, пробрасыать в
# игровой слой события - это уже прираготива Clienapp.

class SpaceDataMgr:
    @property
    def _game_layer(self) -> IGameLayer:
        return ilayer.get_game_layer()

    def set_data(self, space_id: int, key: str, value: str) -> None:
        self._game_layer.call_set_space_data(space_id, key, value)

    def del_data(self, space_id: int, key: str) -> None:
        self._game_layer.call_delete_space_data(space_id, key)
